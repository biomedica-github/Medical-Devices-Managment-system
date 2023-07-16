from rest_framework import serializers
from .models import Proveedor, Contrato, Equipo_medico
from datetime import datetime, date
from datetime import timedelta
numero = 2

class ProveedorSerializers(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['id', 'nombre_proveedor', 'contacto', 'numero_de_contratos']
        
    numero_de_contratos = serializers.SerializerMethodField(method_name='calcular_num_contratos', )

    def calcular_num_contratos(self, proveedor: Proveedor):
        return Contrato.objects.filter(proveedor_id__exact=proveedor.id).count()
    
class ContratoSerializers(serializers.Serializer):
    num_contrato = serializers.CharField(max_length = 100)
    proveedor = serializers.StringRelatedField()
    fecha_vencimiento = serializers.DateField()
    dias_restantes = serializers.SerializerMethodField(method_name='calcular_dias_restantes')
    tipo_contrato = serializers.SerializerMethodField(method_name="tipo_de_contrato")
    tipo_servicio_estipulado = serializers.SerializerMethodField(method_name='tipo_servicio')

    def tipo_servicio(self, contrato: Contrato):
        tipo_servicio = Contrato.objects.filter(num_contrato=contrato.num_contrato).values('tipo_servicio_estipulado').get()
        if tipo_servicio['tipo_servicio_estipulado'] == "PRV":
            return "Mantienimiento de tipo preventivo"
        elif tipo_servicio['tipo_servicio_estipulado'] == "P/C":
            return "Mantenimiento de tipo correctivo y preventivo"
        else:
            return "Contrato no incluye mantenimiento"

    def tipo_de_contrato(self, contrato: Contrato):
        tipo_contrato = Contrato.objects.filter(num_contrato=contrato.num_contrato).values('tipo_contrato').get()
        if tipo_contrato['tipo_contrato'] == "G":
            return "Contrato tipo Garantia"
        elif tipo_contrato['tipo_contrato'] == "C":
            return "Contrato tipo Consolidado"
        else:
            return "Contrato tipo Local"


    def calcular_dias_restantes(self, contrato: Contrato):
        today = date.today()
        fecha_vencimiento_db = Contrato.objects.filter(num_contrato=contrato.num_contrato).values('fecha_vencimiento').get()
        fecha_vencimiento = fecha_vencimiento_db['fecha_vencimiento'] - today
        dias = fecha_vencimiento.days

        if dias < 0:
            return "Contrato vencido"
        else:
            return f"Faltan {dias} dias para el vencimiento"


class Equipo_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo_medico
        fields = ['numero_nacional_inv', 'nombre_equipo', 'modelo', 'estado', 'numero_serie', 'marca', 'cama', 'observaciones', 'contrato','area','cama']
    #contrato = serializers.StringRelatedField()
    area = serializers.StringRelatedField()
    #cama = serializers.StringRelatedField()


