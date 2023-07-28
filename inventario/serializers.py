from rest_framework import serializers
from .models import Proveedor, Contrato, Equipo_medico, Area_hospital, Orden_Servicio
from datetime import datetime, date
from datetime import timedelta




class ContratoProveedor(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = ['num_contrato', 'fecha_vencimiento', 'tipo_contrato', 'dias_restantes']
    tipo_contrato = serializers.SerializerMethodField(method_name="tipo_de_contrato")
   
    dias_restantes = serializers.SerializerMethodField(method_name='calcular_dias_restantes')

    def calcular_dias_restantes(self, contrato: Contrato):
        today = date.today()
        fecha_vencimiento = contrato.fecha_vencimiento - today
        dias = fecha_vencimiento.days

        if dias < 0:
            return "Contrato vencido"
        else:
            return f"Faltan {dias} dias para el vencimiento"
        
    def tipo_de_contrato(self, contrato: Contrato):
        return contrato.get_tipo_contrato_display()


class ProveedorSerializers(serializers.ModelSerializer):
    proveedor_contrato = ContratoProveedor(many= True, read_only = True)
    class Meta:
        model = Proveedor
        fields = ['id','nombre_proveedor', 'contacto', 'proveedor_contrato']    
    
    id = serializers.IntegerField(read_only=True)


class ContratoEquiposSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo_medico
        fields = ['numero_nacional_inv', 'nombre_equipo', 'modelo', 'estado', 'numero_serie', 'marca','area','cama']
    #contrato = serializers.StringRelatedField()
    area = serializers.StringRelatedField()
    #cama = serializers.StringRelatedField()

class ContratoSerializers(serializers.Serializer):
    num_contrato = serializers.CharField(max_length = 100)
    proveedor = serializers.StringRelatedField()
    fecha_vencimiento = serializers.DateField()
    dias_restantes = serializers.SerializerMethodField(method_name='calcular_dias_restantes')
    tipo_contrato = serializers.SerializerMethodField(method_name="tipo_de_contrato")
    tipo_servicio_estipulado = serializers.SerializerMethodField(method_name='tipo_servicio')
    equipos_contrato = ContratoEquiposSerializer(many = True, read_only=True)


    def tipo_servicio(self, contrato: Contrato):
        return contrato.get_tipo_servicio_estipulado_display()

    def tipo_de_contrato(self, contrato: Contrato):
        return contrato.get_tipo_contrato_display()


    def calcular_dias_restantes(self, contrato: Contrato):
        today = date.today()
        fecha_vencimiento = contrato.fecha_vencimiento - today
        dias = fecha_vencimiento.days

        if dias < 0:
            return "Contrato vencido"
        else:
            return f"Faltan {dias} dias para el vencimiento"

class CrearOrdenSerializer(serializers.ModelSerializer):
    estatus = serializers.ChoiceField(choices=Orden_Servicio.ESTATUS_OPCIONES)
    motivo = serializers.ChoiceField(choices=Orden_Servicio.MOTIVO_OPCIONES)
    tipo_orden = serializers.ChoiceField(choices=Orden_Servicio.TIPO_OPCIONES)
    class Meta:
        model = Orden_Servicio
        fields = ['id','numero_orden', 'fecha', 'motivo', 'tipo_orden', 'estatus','responsable','autorizo_jefe_biomedica','autorizo_jefe_conservacion','descripcion_servicio','equipo_complementario','ing_realizo','num_mantenimiento_preventivo','fallo_paciente', 'equipo_medico']
    
    id = serializers.IntegerField(read_only=True)
    extra_kwargs = {'equipo_medico': {'required':False}}

class OrdenEquipoSerializer(serializers.ModelSerializer):

    class Meta: 
        model = Orden_Servicio
        fields = ['id','numero_orden', 'fecha', 'motivo', 'tipo_orden', 'estatus','responsable','autorizo_jefe_biomedica','autorizo_jefe_conservacion','descripcion_servicio','equipo_complementario','ing_realizo','num_mantenimiento_preventivo','fallo_paciente', 'equipo_medico']
    id = serializers.IntegerField(read_only=True)
    tipo_orden = serializers.SerializerMethodField(method_name= 'get_tipo_orden')
    motivo = serializers.SerializerMethodField(method_name= 'get_motivo')
    estatus = serializers.SerializerMethodField(method_name= 'get_estatus')
    extra_kwargs = {'equipo_medico': {'required':False}}

    def get_motivo(self, orden: Orden_Servicio):
        return orden.get_motivo_display()

    def get_tipo_orden(self, orden: Orden_Servicio):
        return orden.get_tipo_orden_display()
    
    def get_estatus(self, orden: Orden_Servicio):
        return orden.get_estatus_display()

class OrdenAgendaSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Orden_Servicio
        fields = ['fecha', 'equipo_medico', 'dias_restantes']
    equipo_medico = serializers.PrimaryKeyRelatedField(many = True, read_only=True)
    dias_restantes = serializers.SerializerMethodField(method_name='calcular_dias_restantes', read_only=True)

    def save(self, **kwargs):
        equipo = self.context['equipo']
        fecha_data = self.validated_data['fecha']
        equipo_med = Equipo_medico.objects.get(numero_nacional_inv=equipo)
        self.instance = orden = Orden_Servicio.objects.create(fecha = fecha_data)
        orden.equipo_medico.add(equipo_med)
        

        return self.instance


    def calcular_dias_restantes(self, orden: Orden_Servicio):
        today = date.today()
        
        fecha_vencimiento = orden.fecha - today
        dias = fecha_vencimiento.days

        if dias <= 0 and orden.estatus == 'PEN':
            return "Orden no atendida, favor de contactar proveedor o actualizar la orden de servicio"
        elif dias <= 0 and orden.estatus != 'PEN':
            return "Servicio atendido"
        else:
            return f"Faltan {dias} para el siguiente servicio"

class Equipo_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Equipo_medico
        fields = ['numero_nacional_inv', 'nombre_equipo', 'modelo', 'estado', 'numero_serie', 'marca', 'observaciones', 'contrato','area','cama']
    #contrato = serializers.StringRelatedField()
    area = serializers.StringRelatedField()
    #cama = serializers.StringRelatedField()

class AreaEquipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo_medico
        fields = ['numero_nacional_inv', 'nombre_equipo', 'modelo', 'marca', 'cama', 'area']

    area = serializers.StringRelatedField()

class AreaSerializer(serializers.ModelSerializer):
    equipos_area = AreaEquipoSerializer(many = True,read_only = True)
    class Meta:
        model = Area_hospital
        fields = ['nombre_sala', 'equipos_area']

class AgregarEquipoAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area_hospital
        fields = ['equipos_area']

class AgregarServicioEquipo(serializers.ModelSerializer):
    estatus = serializers.ChoiceField(choices=Orden_Servicio.ESTATUS_OPCIONES)
    motivo = serializers.ChoiceField(choices=Orden_Servicio.MOTIVO_OPCIONES)
    tipo_orden = serializers.ChoiceField(choices=Orden_Servicio.TIPO_OPCIONES)
    class Meta:
        model = Orden_Servicio
        fields = ['id','numero_orden', 'fecha', 'motivo', 'tipo_orden', 'estatus','responsable','autorizo_jefe_biomedica','autorizo_jefe_conservacion','descripcion_servicio','equipo_complementario','ing_realizo','num_mantenimiento_preventivo','fallo_paciente', 'equipo_medico']
    id = serializers.IntegerField(read_only=True)
    equipo_medico = serializers.PrimaryKeyRelatedField(many = True, read_only=True)

    def save(self, **kwargs):
        equipo = self.context['equipo']
        equipo_med = Equipo_medico.objects.get(numero_nacional_inv=equipo)
        self.instance = orden = Orden_Servicio.objects.create(**self.validated_data)
        orden.equipo_medico.add(equipo_med)
        return self.instance

        
