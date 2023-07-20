from rest_framework import serializers
from .models import Proveedor, Contrato, Equipo_medico, Area_hospital
from datetime import datetime, date
from datetime import timedelta
numero = 2

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
        if contrato.tipo_contrato == "G":
            return "Contrato tipo Garantia"
        elif contrato.tipo_contrato == "C":
            return "Contrato tipo Consolidado"
        else:
            return "Contrato tipo Local"


class ProveedorSerializers(serializers.ModelSerializer):
    proveedor_contrato = ContratoProveedor(many= True, read_only = True)
    class Meta:
        model = Proveedor
        fields = ['id','nombre_proveedor', 'contacto', 'numero_de_contratos', 'proveedor_contrato']    
    numero_de_contratos = serializers.SerializerMethodField(method_name='calcular_num_contratos')

    def calcular_num_contratos(self, proveedor: Proveedor):
        return Contrato.objects.filter(proveedor_id__exact=proveedor.id).count()


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
        if contrato.tipo_servicio_estipulado == "PRV":
            return "Mantienimiento de tipo preventivo"
        elif contrato.tipo_servicio_estipulado == "P/C":
            return "Mantenimiento de tipo correctivo y preventivo"
        else:
            return "Contrato no incluye mantenimiento"

    def tipo_de_contrato(self, contrato: Contrato):
        if contrato.tipo_contrato == "G":
            return "Contrato tipo Garantia"
        elif contrato.tipo_contrato == "C":
            return "Contrato tipo Consolidado"
        else:
            return "Contrato tipo Local"


    def calcular_dias_restantes(self, contrato: Contrato):
        today = date.today()
        fecha_vencimiento = contrato.fecha_vencimiento - today
        dias = fecha_vencimiento.days

        if dias < 0:
            return "Contrato vencido"
        else:
            return f"Faltan {dias} dias para el vencimiento"


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
        fields = ['numero_nacional_inv', 'nombre_equipo', 'modelo', 'marca', 'cama']


class AreaSerializer(serializers.ModelSerializer):
    equipos_area = AreaEquipoSerializer(many = True,read_only = True)
    class Meta:
        model = Area_hospital
        fields = ['nombre_sala', 'equipos_area']
