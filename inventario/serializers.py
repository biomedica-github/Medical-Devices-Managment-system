from rest_framework import serializers
from .models import Proveedor, Contrato, Equipo_medico, Area_hospital, Orden_Servicio, ReporteUsuario, CheckList, Evento
from datetime import datetime, date
from datetime import timedelta
import pytz
from rest_framework.response import Response
from core.models import User
from django.core.validators import FileExtensionValidator
import locale

locale.setlocale(locale.LC_ALL, 'es_ES')

def calcular_fecha(datetimeobject: datetime.date) -> dict:
    return {'dia': datetimeobject.strftime("%A").capitalize(), 
            'dia_numero':datetimeobject.strftime("%d").capitalize(), 
            'mes':datetimeobject.strftime("%B").capitalize(), 
            'año':datetimeobject.strftime("%G").capitalize(),
            'mes_ab':datetimeobject.strftime("%b").upper()}

def calcular_fecha_formato(datetimeobject: datetime.date) -> dict:
    return {'dia': datetimeobject.strftime("%d"),  
            'mes':datetimeobject.strftime("%m").capitalize(), 
            'año':datetimeobject.strftime("%Y").capitalize(),}

def get_time(time:int) -> str:
    if time >= 12:
        return "PM"
    return "AM"

def corta_nombre(falla):
    if falla == "SENSOR":
        return "Falla en sensor"
    elif falla == "NO/TRB":
        return "Equipo no trabaja adecuadamente"
    else:
        return
    


class ContratoProveedor(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = ['id','num_contrato', 'fecha_vencimiento', 'tipo_contrato', 'dias_restantes']
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
        fields = ['id','numero_nacional_inv', 'nombre_equipo', 'modelo', 'estado', 'numero_serie', 'marca','area','cama','contrato']
    contrato = ContratoProveedor(many=False)
    area = serializers.StringRelatedField()
    estado = serializers.SerializerMethodField(method_name='get_estado')

    def get_estado(self, orden: Equipo_medico):
        return orden.get_estado_display()
    #cama = serializers.StringRelatedField()

class ContratoSerializers(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = ['id','num_contrato', 'proveedor', 'fecha_vencimiento', 'dias_restantes', 'tipo_contrato', 'tipo_servicio_estipulado', 'equipos_contrato', 'fecha']
    num_contrato = serializers.CharField(max_length = 100)
    proveedor = serializers.StringRelatedField()
    fecha_vencimiento = serializers.DateField()
    dias_restantes = serializers.SerializerMethodField(method_name='calcular_dias_restantes')
    tipo_contrato = serializers.SerializerMethodField(method_name="tipo_de_contrato")
    tipo_servicio_estipulado = serializers.SerializerMethodField(method_name='tipo_servicio')
    equipos_contrato = ContratoEquiposSerializer(many = True, read_only=True)
    fecha = serializers.SerializerMethodField(method_name='get_fecha')

    def get_fecha(self, contrato:Contrato):
        fecha = contrato.fecha_vencimiento
        return f'{fecha.strftime("%A").capitalize()} {fecha.strftime("%d")} de {fecha.strftime("%B").capitalize()} del {fecha.strftime("%G")}'


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

class ModificarContratoSerializer(serializers.ModelSerializer):
    tipo_contrato = serializers.ChoiceField(choices=Contrato.CONTRATO_OPCIONES)
    tipo_servicio_estipulado = serializers.ChoiceField(choices=Contrato.SERVICIO_OPCIONES)
    class Meta:
        model = Contrato
        fields = ["num_contrato",'proveedor', "fecha_vencimiento", "tipo_contrato", "tipo_servicio_estipulado"]


class CrearContratoSerializer(serializers.ModelSerializer):
    tipo_contrato = serializers.ChoiceField(choices=Contrato.CONTRATO_OPCIONES)
    tipo_servicio_estipulado = serializers.ChoiceField(choices=Contrato.SERVICIO_OPCIONES)
    class Meta:
        model = Contrato
        fields = ["num_contrato", "proveedor", "fecha_vencimiento", "tipo_contrato", "tipo_servicio_estipulado", "equipos_contrato"]
    equipos_contrato = serializers.PrimaryKeyRelatedField(many=True, queryset=Equipo_medico.objects.filter(contrato=None), label= 'Equipos medicos sin contrato')

class AgregarEquipoContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = ["equipos_contrato"]
    equipos_contrato = serializers.PrimaryKeyRelatedField(many=True, queryset=Equipo_medico.objects.filter(contrato=None), label= 'Equipos medicos sin contrato')

    def save(self, **kwargs):
        contrato_pk = self.context['contrato']
        for equipo in self.validated_data['equipos_contrato']:
            equipo_med = Equipo_medico.objects.get(id=equipo)
            equipo_med.contrato = Contrato.objects.get(id=contrato_pk)
            equipo_med.save()
        return self.instance

class AgregarContratoProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = ['num_contrato', 'fecha_vencimiento','tipo_contrato', 'tipo_servicio_estipulado']

    def save(self, **kwargs):
        proveedor_id = self.context['proveedor']
        proveedor_objeto = Proveedor.objects.get(id=proveedor_id)
        self.instance = Contrato.objects.create(proveedor = proveedor_objeto, **self.validated_data)
        return self.instance


class CrearOrdenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orden_Servicio
        fields = ['id','numero_orden', 'fecha', 'motivo', 'tipo_orden', 'estatus','responsable','autorizo_jefe_biomedica','autorizo_jefe_conservacion','descripcion_servicio','equipo_complementario','ing_realizo','num_mantenimiento_preventivo','fallo_paciente', 'equipo_medico', 'orden_escaneada']
    

    ESTATUS_FUERA = 'OUT'
    ESTATUS_FUNCIONAL = 'FUN'
    ESTATUS_NO_SERVICIO = 'N/A'
    ESTATUS_OPCIONES = [
        (ESTATUS_FUNCIONAL, 'Equipo funcional'),
        (ESTATUS_FUERA, 'Equipo fuera de servicio'),
        (ESTATUS_NO_SERVICIO, 'No se realizo servicio')
    ]

    estatus = serializers.ChoiceField(choices=ESTATUS_OPCIONES)
    motivo = serializers.ChoiceField(choices=Orden_Servicio.MOTIVO_OPCIONES)
    tipo_orden = serializers.ChoiceField(choices=Orden_Servicio.TIPO_OPCIONES)
    id = serializers.IntegerField(read_only=True)
    orden_escaneada = serializers.FileField(validators=[FileExtensionValidator(allowed_extensions=['pdf'])], required=False)
    extra_kwargs = {'equipo_medico': {'required':False}}

class OrdenServicioSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Orden_Servicio
        fields = '__all__'
    id = serializers.IntegerField(read_only=True)
    tipo_orden = serializers.SerializerMethodField(method_name= 'get_tipo_orden')
    motivo = serializers.SerializerMethodField(method_name= 'get_motivo')
    estatus = serializers.SerializerMethodField(method_name= 'get_estatus')
    orden_escaneada = serializers.FileField(validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    equipo_medico = serializers.StringRelatedField()

    def get_motivo(self, orden: Orden_Servicio):
        return orden.get_motivo_display()

    def get_tipo_orden(self, orden: Orden_Servicio):
        return orden.get_tipo_orden_display()
    
    def get_estatus(self, orden: Orden_Servicio):
        return orden.get_estatus_display()

class OrdenEquipoSerializer(serializers.ModelSerializer):

    class Meta: 
        model = Orden_Servicio
        fields = '__all__'
    id = serializers.IntegerField(read_only=True)
    tipo_orden = serializers.SerializerMethodField(method_name= 'get_tipo_orden')
    motivo = serializers.SerializerMethodField(method_name= 'get_motivo')
    estatus = serializers.SerializerMethodField(method_name= 'get_estatus')
    orden_escaneada = serializers.FileField(validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    extra_kwargs = {'equipo_medico': {'required':False}}
    equipo_medico = ContratoEquiposSerializer(many=True, read_only=True)

    def get_motivo(self, orden: Orden_Servicio):
        return orden.get_motivo_display()

    def get_tipo_orden(self, orden: Orden_Servicio):
        return orden.get_tipo_orden_display()
    
    def get_estatus(self, orden: Orden_Servicio):
        return orden.get_estatus_display()

class EquiposAgendaAreaUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo_medico
        fields = ['id','numero_nacional_inv', 'nombre_equipo', 'area', 'cama']
    area = serializers.StringRelatedField()

class AgregarEventoEquipoSerializer(serializers.ModelSerializer):
    TIPO_SERVICIO = "SERVC"
    TIPO_CAPACITACION = "CAPAC"
    TIPO_CHECKLIST = "CHECK"
    TIPO_OPCIONES = [
        (TIPO_SERVICIO, "Servicio preventivo agendado"),
        (TIPO_CAPACITACION, "Curso de capacitacion agendada"),
        (TIPO_CHECKLIST, "Chequeo al equipo agendado"),
    ]

    tipo_evento = serializers.ChoiceField(choices=TIPO_OPCIONES)
    class Meta:
        model = Evento
        fields = ['fecha', 'tipo_evento']

    def save(self, **kwargs):
        equipo = self.context['equipo']
        equipo_med = Equipo_medico.objects.get(id=equipo)
        self.instance = orden = Evento.objects.create(equipo_medico=equipo_med, **self.validated_data)
        return self.instance



class AgregarEventoSerializer(serializers.ModelSerializer):
    TIPO_SERVICIO = "SERVC"
    TIPO_CAPACITACION = "CAPAC"
    TIPO_CHECKLIST = "CHECK"
    TIPO_OPCIONES = [
        (TIPO_SERVICIO, "Servicio preventivo agendado"),
        (TIPO_CAPACITACION, "Curso de capacitacion agendada"),
        (TIPO_CHECKLIST, "Chequeo al equipo agendado"),
    ]

    tipo_evento = serializers.ChoiceField(choices=TIPO_OPCIONES)
    class Meta:
        model = Evento
        fields = ['fecha', 'equipo_medico', 'tipo_evento']


class AgendaAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = ['id','fecha', 'equipo_medico','tipo_evento', 'fecha_read', 'dias_restantes_num', 'contrato', 'contrato_href']
    fecha_read = serializers.SerializerMethodField(method_name='get_fecha')
    equipo_medico = EquiposAgendaAreaUsuarioSerializer()
    tipo_evento = serializers.SerializerMethodField(method_name='get_tipo')
    contrato = serializers.StringRelatedField()
    contrato_href = serializers.SerializerMethodField(method_name='get_contrato')
    dias_restantes_num = serializers.SerializerMethodField(method_name='get_dias_faltan', read_only=True)

    def get_contrato(self, evento:Evento):
        return evento.contrato

    def get_tipo(self, evento: Evento):
        return evento.get_tipo_evento_display()

    def get_dias_faltan(self, orden: Evento):
        today = date.today()
        
        fecha_vencimiento = orden.fecha - today
        dias = fecha_vencimiento.days

        return dias

    def get_fecha(self, orden: Evento):
        fecha_str = calcular_fecha(orden.fecha)
        return fecha_str

    
class OrdenAgendaAreaUsuarioVerSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Orden_Servicio
        fields = ['id','fecha', 'equipo_medico', 'dias_restantes', 'fecha_read', 'dias_restantes_num']
    fecha_read = serializers.SerializerMethodField(method_name='get_fecha')
    equipo_medico = EquiposAgendaAreaUsuarioSerializer(many = True, read_only=True)
    dias_restantes = serializers.SerializerMethodField(method_name='calcular_dias_restantes', read_only=True)
    dias_restantes_num = serializers.SerializerMethodField(method_name='get_dias_faltan', read_only=True)

    def save(self, **kwargs):
        validated_data = {**self.validated_data, **kwargs}
        if self.instance is not None:
            self.instance = self.update(self.instance, validated_data)
            assert self.instance is not None, (
                '`update()` did not return an object instance.'
            )
        else:
            equipo = self.context['equipo']
            fecha_data = self.validated_data['fecha']
            equipo_med = Equipo_medico.objects.get(id=equipo)
            contrato_equipo = Equipo_medico.objects.values('contrato').get(id = equipo)
            contrato_objeto = Contrato.objects.get(id = contrato_equipo['contrato'])
            
            self.instance = orden = Orden_Servicio.objects.create(fecha = fecha_data, contrato = contrato_objeto)
            orden.equipo_medico.add(equipo_med)
        
        return self.instance

    def get_dias_faltan(self, orden: Orden_Servicio):
        today = date.today()
        
        fecha_vencimiento = orden.fecha - today
        dias = fecha_vencimiento.days

        return dias

    def get_fecha(self, orden:Orden_Servicio):
        fecha_str = calcular_fecha(orden.fecha)
        return fecha_str


    def calcular_dias_restantes(self, orden: Orden_Servicio):
        today = date.today()
        
        fecha_vencimiento = orden.fecha - today
        dias = fecha_vencimiento.days

        if dias <= 0 and orden.estatus == 'PEN':
            return "Orden no atendida, favor de contactar proveedor o actualizar la orden de servicio"
        elif dias <= 0 and orden.estatus != 'PEN':
            return "Servicio atendido"
        else:
            return f"Faltan {dias} dias para el siguiente servicio"

class EquipoOrdenAgendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo_medico
        fields = ['id', 'numero_nacional_inv', 'nombre_equipo']


class OrdenAgendaSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Orden_Servicio
        fields = ['id','fecha', 'equipo_medico', 'dias_restantes', 'fecha_read', 'dias_restantes_num']
    fecha_read = serializers.SerializerMethodField(method_name='get_fecha')
    equipo_medico = serializers.StringRelatedField(many = True, read_only=True)
    dias_restantes = serializers.SerializerMethodField(method_name='calcular_dias_restantes', read_only=True)
    dias_restantes_num = serializers.SerializerMethodField(method_name='get_dias_faltan', read_only=True)

    def save(self, **kwargs):
        validated_data = {**self.validated_data, **kwargs}
        if self.instance is not None:
            self.instance = self.update(self.instance, validated_data)
            assert self.instance is not None, (
                '`update()` did not return an object instance.'
            )
        else:
            equipo = self.context['equipo']
            fecha_data = self.validated_data['fecha']
            equipo_med = Equipo_medico.objects.get(id=equipo)
            contrato_equipo = Equipo_medico.objects.values('contrato').get(id = equipo)
            contrato_objeto = Contrato.objects.get(id = contrato_equipo['contrato'])
            
            self.instance = orden = Orden_Servicio.objects.create(fecha = fecha_data, contrato = contrato_objeto)
            orden.equipo_medico.add(equipo_med)
        
        return self.instance

    def get_dias_faltan(self, orden: Orden_Servicio):
        today = date.today()
        
        fecha_vencimiento = orden.fecha - today
        dias = fecha_vencimiento.days

        return dias

    def get_fecha(self, orden:Orden_Servicio):
        fecha_str = calcular_fecha(orden.fecha)
        return fecha_str


    def calcular_dias_restantes(self, orden: Orden_Servicio):
        today = date.today()
        
        fecha_vencimiento = orden.fecha - today
        dias = fecha_vencimiento.days

        if dias <= 0 and orden.estatus == 'PEN':
            return "Orden no atendida, favor de contactar proveedor o actualizar la orden de servicio"
        elif dias <= 0 and orden.estatus != 'PEN':
            return "Servicio atendido"
        else:
            return f"Faltan {dias} dias para el siguiente servicio"

class AgregarOrdenAgendaAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orden_Servicio
        fields = ['fecha', 'equipo_medico']

class VerEquipoOrdenAgendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo_medico
        fields = ['numero_nacional_inv', 'nombre_equipo', 'cama']



class OrdenAgendaAreaSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Orden_Servicio
        fields = ['id','fecha', 'equipo_medico', 'dias_restantes']
    equipo_medico = VerEquipoOrdenAgendaSerializer(many = True, read_only=True)
    dias_restantes = serializers.SerializerMethodField(method_name='calcular_dias_restantes', read_only=True)

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
    cama = serializers.IntegerField(required =False, allow_null=True)
    class Meta:
        model = Equipo_medico
        fields = ['numero_nacional_inv', 'nombre_equipo', 'modelo', 'estado', 'numero_serie', 'marca', 'observaciones', 'contrato','area', 'cama']

        extra_kwargs = {'area': {'required': False}}


class CrearEquipoAreaSerializer(serializers.ModelSerializer):
    cama = serializers.IntegerField(required =False, allow_null=True)
    class Meta:
        model = Equipo_medico
        fields = ['numero_nacional_inv', 'nombre_equipo', 'modelo', 'estado', 'numero_serie', 'marca', 'observaciones', 'contrato', 'cama']

    def save(self, **kwargs):
        area = Area_hospital.objects.get(id = self.context['area'])
        self.instace = Equipo_medico.objects.create(area = area, **self.validated_data)
        return self.instance



class EquipoBajaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo_medico
        fields = ['carta_obsolescencia_tercero','dictamen_tecnico_propio','minuta_baja']
    carta_obsolescencia_tercero = serializers.FileField(validators=[FileExtensionValidator(allowed_extensions=['pdf'])], allow_null=True)
    dictamen_tecnico_propio = serializers.FileField(validators=[FileExtensionValidator(allowed_extensions=['pdf'])], allow_null=True)
    minuta_baja = serializers.FileField(validators=[FileExtensionValidator(allowed_extensions=['pdf'])], allow_null=True)



class Equipo_Serializer(serializers.ModelSerializer):
    cama = serializers.IntegerField(required =False, allow_null=True)
    class Meta:
        model = Equipo_medico
        fields = ['id','numero_nacional_inv', 'nombre_equipo', 'modelo', 'estado', 'numero_serie', 'marca', 'observaciones', 'contrato','area','cama','area_href','contrato_href',
                   'carta_obsolescencia_tercero', 'dictamen_tecnico_propio', 'minuta_baja']
    contrato = serializers.StringRelatedField()
    area = serializers.StringRelatedField()
    estado = serializers.SerializerMethodField(method_name='get_estado', read_only=True)
    area_href = serializers.SerializerMethodField(method_name='get_area', read_only=True)
    contrato_href = serializers.SerializerMethodField(method_name='get_contrato', read_only=True)
    

    def get_contrato(self, equipo: Equipo_medico):
        return equipo.contrato

    def get_area(self, equipo: Equipo_medico):
        return equipo.area
    
    def get_estado(self, equipo: Equipo_medico):
        return equipo.get_estado_display()
    #cama = serializers.StringRelatedField()

class AreaEquipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo_medico
        fields = ['id','numero_nacional_inv', 'nombre_equipo', 'modelo', 'marca', 'cama', 'area', 'estado']
    estado = serializers.SerializerMethodField(method_name='get_estado')
    area = serializers.StringRelatedField()

    def get_estado(self, equipo: Equipo_medico):
        return equipo.get_estado_display()

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area_hospital
        fields = ['id','nombre_sala', 'responsable']
    responsable = serializers.StringRelatedField(many=True)
    

class AgregarEquipoAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area_hospital
        fields = ['id','nombre_sala','equipos_area', 'responsable']
    equipos_area = serializers.PrimaryKeyRelatedField(many=True, queryset=Equipo_medico.objects.filter(area=None), label= 'Equipos medicos sin area establecida')
    

class AgregarServicioEquipo(serializers.ModelSerializer):
    estatus = serializers.ChoiceField(choices=Orden_Servicio.ESTATUS_OPCIONES)
    motivo = serializers.ChoiceField(choices=Orden_Servicio.MOTIVO_OPCIONES)
    tipo_orden = serializers.ChoiceField(choices=Orden_Servicio.TIPO_OPCIONES)
    class Meta:
        model = Orden_Servicio
        fields = ['id','numero_orden', 'fecha', 'motivo', 'tipo_orden', 'estatus','responsable','autorizo_jefe_biomedica','autorizo_jefe_conservacion','descripcion_servicio','equipo_complementario','ing_realizo','num_mantenimiento_preventivo','fallo_paciente', 'orden_escaneada','equipo_medico']
    id = serializers.IntegerField(read_only=True)
    equipo_medico = serializers.PrimaryKeyRelatedField(many = True, read_only=True)

    def save(self, **kwargs):
        equipo = self.context['equipo']
        equipo_med = Equipo_medico.objects.get(id=equipo)
        self.instance = orden = Orden_Servicio.objects.create(**self.validated_data)
        orden.equipo_medico.add(equipo_med)
        return self.instance


class CrearNuevoCheckListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckList
        fields = ['id','bateria','condicion_general', 'enciende', 'sensor_SPO2',
                  'sensor_TEMP','PANI','sensor_ECG','sensor_PAI','observaciones',
                  'desempeño_general', 'equipo']

class UpdateCheckListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckList
        fields = ['id','bateria','condicion_general', 'enciende', 'sensor_SPO2',
                  'sensor_TEMP','PANI','sensor_ECG','sensor_PAI','observaciones',
                  'desempeño_general']
    


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
        equipo_query = Equipo_medico.objects.get(id=equipo_med)
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
        equipo_query = Equipo_medico.objects.get(id=equipo_med)
        usuario_context = self.context['usuario']
        usuario = User.objects.get(id=usuario_context)


        self.instance = ReporteUsuario.objects.create(area=sala_query, equipo=equipo_query, responsable=usuario, **self.validated_data)
        return self.instance
    
class CrearAtenderReporteSerializer(serializers.ModelSerializer): 
    class Meta:
        model = ReporteUsuario
        fields = ['id','falla', 'descripcion','solucion_tecnico','equipo_complementario']
    
    id = serializers.IntegerField(read_only=True)
    
    def save(self, **kwargs):
        if self.context['area'] != "no":
            area_equipo = self.context['area']
            sala_query = Area_hospital.objects.get(id=area_equipo)
        else:
            sala_query = None
        equipo_med = self.context['equipo']
        equipo_query = Equipo_medico.objects.get(id=equipo_med)
        usuario_context = self.context['usuario']
        usuario = User.objects.get(id=usuario_context)


        self.instance = ReporteUsuario.objects.create(area=sala_query, equipo=equipo_query, responsable=usuario, estado ='CER', **self.validated_data)
        return self.instance

class VerReportesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteUsuario
        fields = '__all__'
    area = serializers.StringRelatedField()
    #equipo = serializers.StringRelatedField()
    estado = serializers.SerializerMethodField(method_name='get_estado')
    falla = serializers.SerializerMethodField()
    responsable = serializers.StringRelatedField()
    fecha_str= serializers.SerializerMethodField(method_name='get_fecha')
    hora= serializers.SerializerMethodField(method_name='get_hora')
    equipo= ContratoEquiposSerializer(many=False, read_only=True)
    corto= serializers.SerializerMethodField(method_name="get_nombreCorto")
    areaid= serializers.SerializerMethodField(method_name="get_id")
    fecha_entrega_str = serializers.SerializerMethodField(method_name="get_fecha_entrega")
    hora_entrega = serializers.SerializerMethodField(method_name="get_hora_entrega")

    def get_fecha_entrega(self, reporte: ReporteUsuario):
        entrega = reporte.fecha_entrega
        if entrega == None:
            return "2023-10-23T12:00:00"
        else:    
            fecha = calcular_fecha(reporte.fecha_entrega)

        return f"{fecha['dia']} {fecha['dia_numero']} de {fecha['mes']} del año {fecha['año']}"
    
    def get_hora_entrega(self, reporte: ReporteUsuario):
        entrega = reporte.fecha_entrega
        if entrega == None:
            return "12:00"
        else:
            hora = reporte.fecha_entrega

            time = get_time(hora.hour)

            hora_str= hora.strftime("%I:%M %p")

        return hora_str + time

    def get_id(self, reporte: ReporteUsuario):
        if reporte.equipo.area is not None:
            return reporte.equipo.area.id
        else:
            return 0


    def get_falla(self, reporte: ReporteUsuario):
        return reporte.get_falla_display()

    def get_estado(self, reporte: ReporteUsuario):
        return reporte.get_estado_display()
    
    def get_fecha(self, reporte: ReporteUsuario):
        fecha = calcular_fecha(reporte.fecha_hora)
        
        
        return f"{fecha['dia']} {fecha['dia_numero']} de {fecha['mes']} del año {fecha['año']}"

    def get_hora(self, reporte:ReporteUsuario):
        hora = reporte.fecha_hora

        time = get_time(hora.hour)

        hora_str= hora.strftime("%I:%M %p")

        return hora_str + time
    
    def get_nombreCorto(self, reporte: ReporteUsuario):
        corto=corta_nombre(reporte.falla)
        return corto

class verOrdenReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model= Orden_Servicio
        fields= ['numero_orden', 'equipo_complementario']

class AgregarOrdenTicketsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Orden_Servicio
        fields=['equipo_complementario']

class VerReportesPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteUsuario
        fields = '__all__'
    area = serializers.StringRelatedField()
    #equipo = serializers.StringRelatedField()
    estado = serializers.SerializerMethodField(method_name='get_estado')
    falla = serializers.SerializerMethodField()
    responsable = serializers.StringRelatedField()
    fecha_str= serializers.SerializerMethodField(method_name='get_fecha')
    hora= serializers.SerializerMethodField(method_name='get_hora')
    equipo= ContratoEquiposSerializer(many=False, read_only=True)
    corto= serializers.SerializerMethodField(method_name="get_nombreCorto")
    orden = verOrdenReporteSerializer(many=False,read_only=True)
    fecha_entrega_str = serializers.SerializerMethodField(method_name="get_fecha_entrega")
    hora_entrega = serializers.SerializerMethodField(method_name="get_hora_entrega")

    def get_fecha_entrega(self, reporte: ReporteUsuario):
        fecha = calcular_fecha_formato(reporte.fecha_entrega)

        return f"{fecha['año']}-{fecha['mes']}-{fecha['dia']}"
    
    def get_hora_entrega(self, reporte: ReporteUsuario):
        hora = reporte.fecha_entrega

        time = get_time(hora.hour)

        hora_str= hora.strftime("%I:%M %p")

        return hora_str + time
    def get_falla(self, reporte: ReporteUsuario):
        return reporte.get_falla_display()

    def get_estado(self, reporte: ReporteUsuario):
        return reporte.get_estado_display()
    
    def get_fecha(self, reporte: ReporteUsuario):
        fecha = calcular_fecha_formato(reporte.fecha_hora)
        
        
        return f"{fecha['año']}-{fecha['mes']}-{fecha['dia']}"

    def get_hora(self, reporte:ReporteUsuario):
        hora = reporte.fecha_hora

        time = get_time(hora.hour)

        hora_str= hora.strftime("%I:%M %p")

        return hora_str + time
    
    def get_nombreCorto(self, reporte: ReporteUsuario):
        corto=corta_nombre(reporte.falla)
        return corto

class AtenderReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteUsuario
        fields = ['solucion_tecnico','equipo_complementario']

    # def save(self, **kwargs):
    #     ticket_id = self.context['ticket']
    #     self.instance = ReporteUsuario.objects.filter(id=ticket_id).update(estado='COM', **self.validated_data)
    #     return self.instance


class CheckListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckList
        fields = '__all__'
    
    equipo = serializers.StringRelatedField()
    area = serializers.StringRelatedField()
    hora = serializers.SerializerMethodField(method_name='get_hora')
    fecha_str = serializers.SerializerMethodField(method_name='get_fecha')
    bateria = serializers.SerializerMethodField(method_name='get_bateria')
    condicion_general = serializers.SerializerMethodField(method_name='get_condic')
    sensor_SPO2 = serializers.SerializerMethodField(method_name='get_spo2')
    sensor_TEMP = serializers.SerializerMethodField(method_name='get_temp')
    PANI = serializers.SerializerMethodField(method_name='get_pani')
    sensor_ECG = serializers.SerializerMethodField(method_name='get_ecg')
    sensor_PAI = serializers.SerializerMethodField(method_name='get_pai')
    rango = serializers.SerializerMethodField(method_name='get_rango')
    prueba_funcionamiento = serializers.SerializerMethodField(method_name='get_prueba')
    extra_kwargs = {'sala': {'required': True}, 'equipo': {'required':True}}

    def get_prueba(self, checklist:CheckList):
        return checklist.get_prueba_funcionamiento_display()

    def get_rango(self, checklist:CheckList):
        return range(checklist.desempeño_general)

    def get_bateria(self, checklist:CheckList):
        return checklist.get_bateria_display()
    
    def get_condic(self, checklist:CheckList):
        return checklist.get_condicion_general_display()
    
    def get_spo2(self, checklist:CheckList):
        return checklist.get_sensor_SPO2_display()
    
    def get_temp(self, checklist:CheckList):
        return checklist.get_sensor_TEMP_display()
    
    def get_pani(self, checklist:CheckList):
        return checklist.get_PANI_display()
    
    def get_ecg(self, checklist:CheckList):
        return checklist.get_sensor_ECG_display()
    
    def get_pai(self, checklist:CheckList):
        return checklist.get_sensor_PAI_display()
    
    def get_fecha(self, checklist:CheckList):
        fecha = calcular_fecha(checklist.fecha_hora)
        
        
        return f"{fecha['dia']} {fecha['dia_numero']} de {fecha['mes']} del año {fecha['año']}"

    def get_hora(self, checklist:CheckList):
        hora = checklist.fecha_hora

        time = get_time(hora.hour)

        hora_str= hora.strftime("%I:%M %p")

        return hora_str + time


    def save(self, **kwargs):
        return super().save(**kwargs)



