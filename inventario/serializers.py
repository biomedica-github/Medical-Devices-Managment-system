from rest_framework import serializers
from .models import Proveedor, Contrato, Equipo_medico, Area_hospital, Orden_Servicio, Cama, ReporteUsuario, CheckList
from datetime import datetime, date
from datetime import timedelta
import pytz
from rest_framework.response import Response
from core.models import User



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
        
class CrearContratoSerializer(serializers.ModelSerializer):
    tipo_contrato = serializers.ChoiceField(choices=Contrato.CONTRATO_OPCIONES)
    tipo_servicio_estipulado = serializers.ChoiceField(choices=Contrato.SERVICIO_OPCIONES)
    class Meta:
        model = Contrato
        fields = ["num_contrato", "proveedor", "fecha_vencimiento", "tipo_contrato", "tipo_servicio_estipulado", 'equipos_contrato']
    extra_kwargs = {'proveedor': {'required':True}, 'equipos': {'required':False}}


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


class AgendaAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orden_Servicio
        fields = ['id','fecha', 'equipo_medico', 'dias_restantes']
    dias_restantes = serializers.SerializerMethodField(method_name='calcular_dias_restantes', read_only=True)
    extra_kwargs = {'equipo_medico': {'required': True}}

    def calcular_dias_restantes(self, orden: Orden_Servicio):
        fecha = datetime.today()
        tz = pytz.timezone('America/Los_Angeles')
        today = fecha.astimezone(tz=tz).date()
        fecha_vencimiento = orden.fecha - today
        dias = fecha_vencimiento.days

        if dias < 0 and orden.estatus == 'PEN':
            return "Orden no atendida, favor de contactar proveedor o actualizar la orden de servicio"
        if dias == 0 and orden.estatus == 'PEN':
            return "Hoy se debe atender la orden, favor de contactar a su proveedor y confirmar"
        elif dias <= 0 and orden.estatus != 'PEN':
            return "Servicio atendido"
        else:
            return f"Faltan {dias} para el siguiente servicio"


class OrdenAgendaSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Orden_Servicio
        fields = ['id','fecha', 'equipo_medico', 'dias_restantes']
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


class CrearEquipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo_medico
        fields = ['numero_nacional_inv', 'nombre_equipo', 'modelo', 'estado', 'numero_serie', 'marca', 'observaciones', 'contrato','area','cama']

        extra_kwargs = {'area': {'required': False}}

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
        fields = ['nombre_sala', 'responsable', 'equipos_area']

class AgregarEquipoAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area_hospital
        fields = ['equipos_area', 'responsable']
    extra_kwargs = {'responsable': {'required':False}}

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

class PutCamaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cama
        fields = ['equipos_cama']
    extra_kwargs = {'equipos': {'required':False}}

    def save(self, **kwargs):
        cama = self.context['cama']
        area = self.context['area']
        print(self.validated_data)
        equipos = self.validated_data['equipos_cama']
        self.instance = cama_area = Cama.objects.filter(numero_cama = cama, sala=area).get()
        for equipo in equipos:
            cama_area.equipos_cama.add(equipo)

        return self.instance

class CrearCheckListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckList
        fields = ['id','bateria','condicion_general', 'enciende', 'sensor_SPO2',
                  'sensor_TEMP','PANI','sensor_ECG','sensor_PAI','observaciones',
                  'desempeño_general']

    def save(self, **kwargs):
        sala = self.context['area']
        sala_query = Area_hospital.objects.get(id=sala)
        equipo_med = self.context['equipo']
        equipo_query = Equipo_medico.objects.get(numero_nacional_inv=equipo_med)
        CheckList.objects.create(area=sala_query, equipo = equipo_query, **self.validated_data)
        return self.instance

class CrearReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteUsuario
        fields = ['id','falla', 'descripcion']
    
    id = serializers.IntegerField(read_only=True)
    
    def save(self, **kwargs):
        area_equipo = self.context['area']
        sala_query = Area_hospital.objects.get(id=area_equipo)
        equipo_med = self.context['equipo']
        equipo_query = Equipo_medico.objects.get(numero_nacional_inv=equipo_med)
        usuario_context = self.context['usuario']
        usuario = User.objects.get(id=usuario_context)


        self.instance = ReporteUsuario.objects.create(area=sala_query, equipo=equipo_query, responsable=usuario, **self.validated_data)
        return self.instance

class VerReportesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteUsuario
        fields = '__all__'
    area = serializers.StringRelatedField()
    equipo = serializers.StringRelatedField()
    estado = serializers.SerializerMethodField(method_name='get_estado')
    falla = serializers.SerializerMethodField()
    responsable = serializers.StringRelatedField()
    def get_falla(self, reporte: ReporteUsuario):
        return reporte.get_falla_display()

    def get_estado(self, reporte: ReporteUsuario):
        return reporte.get_estado_display()

class AtenderReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteUsuario
        fields = ['estado', 'solucion_tecnico']



class CheckListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckList
        fields = '__all__'
    sala = serializers.StringRelatedField()
    extra_kwargs = {'sala': {'required': True}, 'equipo': {'required':True}}
    
class GetCamaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cama
        fields = ['numero_cama', 'equipos_cama']

class CrearCamaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cama
        fields = ['numero_cama', 'sala', 'equipos_cama']
    extra_kwargs = {'sala': {'required':True}, 'equipos':{'required':True}}       
