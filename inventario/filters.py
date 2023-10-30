from . import models
import django_filters
from datetime import date
from django_filters.rest_framework import backends
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field

fecha_choices = [
        (1, 'Enero'),
        (2, 'Febrero'),
        (3, 'Marzo'),
        (4, 'Abril'),
        (5, 'Mayo'),
        (6, 'Junio'),
        (7, 'Julio'),
        (8, 'Agosto'),
        (9, 'Septiembre'),
        (10, 'Octubre'),
        (11, 'Noviembre'),
        (12, 'Diciembre')
    ]



class filtro_proveedor(django_filters.FilterSet):
    nombre_proveedor = django_filters.CharFilter(field_name='nombre_proveedor', lookup_expr='icontains', label= 'Nombre del proveedor')
    class Meta:
        model = models.Proveedor
        fields = ['nombre_proveedor']
        


class filtro_equipo(django_filters.FilterSet):
    numero_nacional_inv = django_filters.CharFilter(field_name='numero_nacional_inv', lookup_expr='icontains', label= 'Numero nacional de inventario')
    nombre_equipo = django_filters.CharFilter(field_name='nombre_equipo', lookup_expr='icontains', label='Nombre del equipo')
    marca = django_filters.CharFilter(field_name='marca', lookup_expr='icontains', label='Marca del equipo')
    modelo = django_filters.CharFilter(field_name='modelo', lookup_expr='icontains', label='Modelo del equipo')
    numero_serie = django_filters.CharFilter(field_name='numero_serie', lookup_expr='icontains', label='Numero de serie del equipo')
    
    class Meta:
        model = models.Equipo_medico
        fields = ['marca', 'modelo', 'area', 'contrato', 'numero_serie', 'estado', 'nombre_equipo', 'numero_nacional_inv', 'cama']
    

class filtro_equipo_servicio(django_filters.FilterSet):
    mes_servicio = django_filters.ChoiceFilter(choices=fecha_choices, field_name='fecha', lookup_expr='month', label='Mes cuando se realizo servicio')
    año_servicio = django_filters.NumberFilter(field_name='fecha', lookup_expr='year', label= 'Año en que se realizo servicio')
    numero_orden = django_filters.CharFilter(field_name='numero_orden', lookup_expr='icontains', label='Numero de orden de servicio')
    
    class Meta:
        model = models.Orden_Servicio
        fields = ['motivo', 'tipo_orden']
    

class filtro_equipo_agenda(django_filters.FilterSet):
    mes = django_filters.ChoiceFilter(choices=fecha_choices, field_name='fecha', lookup_expr='month', label='Mes')
    año = django_filters.NumberFilter(field_name='fecha', lookup_expr='year', label= 'Año')
    rango = django_filters.DateRangeFilter(label='Rango de fechas')

    class Meta:
        model = models.Orden_Servicio
        fields = ['mes','año', 'fecha', 'rango']


class filtro_agenda(django_filters.FilterSet):
    
    mes = django_filters.ChoiceFilter(choices=fecha_choices, field_name='fecha', lookup_expr='month', label='Mes')
    año = django_filters.NumberFilter(field_name='fecha', lookup_expr='year', label='Año')
    shortcut = django_filters.DateRangeFilter(field_name='fecha',label="Atajos de fecha")

    class Meta:
        model = models.Evento
        fields = ['mes', 'fecha', 'año', 'shortcut', 'tipo_evento']


class filtro_equipo_checklist(django_filters.FilterSet):
    mes = django_filters.ChoiceFilter(choices=fecha_choices, field_name='fecha_hora', lookup_expr='month', label='Mes')
    dia = django_filters.NumberFilter(field_name='fecha_hora', lookup_expr='day', label='Dia')
    año = django_filters.NumberFilter(field_name='fecha_hora', lookup_expr='year', label='Año')
    
    class Meta:
        model = models.CheckList
        fields = ['mes', 'dia', 'año']

class filtro_contrato(django_filters.FilterSet):
    num_contrato = django_filters.CharFilter(field_name='num_contrato', lookup_expr='icontains', label= 'Numero de contrato')
    año_vencimiento = django_filters.NumberFilter(field_name='fecha_vencimiento', lookup_expr='year', label= 'Año de vencimiento')
    mes_vencimiento = django_filters.ChoiceFilter(choices=fecha_choices,field_name='fecha_vencimiento', lookup_expr='month', label= 'Mes de vencimiento')

    class Meta:
        model = models.Contrato
        fields = ['tipo_contrato', 'num_contrato', 'fecha_vencimiento', 'tipo_servicio_estipulado', 'proveedor', 'año_vencimiento', 'mes_vencimiento']

class filtro_ordenservicio(django_filters.FilterSet):
    mes_servicio = django_filters.ChoiceFilter(choices=fecha_choices, field_name='fecha', lookup_expr='month', label='Mes cuando se realizo servicio')
    año_servicio = django_filters.NumberFilter(field_name='fecha', lookup_expr='year', label= 'Año en que se realizo servicio')
    numero_orden = django_filters.CharFilter(field_name='numero_orden', lookup_expr='icontains', label='Numero de orden de servicio')
    
    class Meta:
        model = models.Orden_Servicio
        fields = ['fecha','motivo', 'tipo_orden', 'estatus', 'equipo_medico']

class filtro_ordenarea(django_filters.FilterSet):
    mes_servicio = django_filters.ChoiceFilter(choices=fecha_choices, field_name='fecha', lookup_expr='month', label='Mes cuando se realizo servicio')
    año_servicio = django_filters.NumberFilter(field_name='fecha', lookup_expr='year', label= 'Año en que se realizo servicio')
    numero_orden = django_filters.CharFilter(field_name='numero_orden', lookup_expr='icontains', label='Numero de orden de servicio')
    
    class Meta:
        model = models.Orden_Servicio
        fields = ['fecha','motivo', 'tipo_orden', 'estatus']

class filtro_ordenpendiente(django_filters.FilterSet):
    mes_servicio = django_filters.ChoiceFilter(choices=fecha_choices, field_name='fecha', lookup_expr='month', label='Mes')
    año_servicio = django_filters.NumberFilter(field_name='fecha', lookup_expr='year', label= 'Año')
    prueba = django_filters.BooleanFilter(field_name='fecha', method='filtro_vencido', label='Mostrar solo ordenes pasadas de fecha')
    class Meta:
        model = models.Orden_Servicio
        fields = ['equipo_medico']

    def filtro_vencido(self, queryset, name, value):
        hoy = date.today()
        if value == True:
            return queryset.filter(fecha__lt=hoy)
        return queryset

class filtro_reportes(django_filters.FilterSet):
    mes = django_filters.ChoiceFilter(choices=fecha_choices, field_name='fecha_hora', lookup_expr='month', label='Mes')
    dia = django_filters.NumberFilter(field_name='fecha_hora', lookup_expr='day', label='Dia')
    año = django_filters.NumberFilter(field_name='fecha_hora', lookup_expr='year', label= 'Año')

    class Meta:
        model = models.ReporteUsuario
        fields = ['area', 'equipo', 'falla']

class filtro_areas_general(django_filters.FilterSet):
    nombre_sala = django_filters.CharFilter(field_name='nombre_sala', lookup_expr='icontains', label='Nombre de la sala')

    class Meta:
        model = models.Area_hospital
        fields = ['nombre_sala']

class filtro_areas_equipo(django_filters.FilterSet):
    cama = django_filters.NumberFilter(field_name='cama', lookup_expr='exact', label='Cama donde se encuentra el equipo')
    numero_nacional_inv = django_filters.CharFilter(field_name='numero_nacional_inv', lookup_expr='icontains', label= 'Numero nacional de inventario')
    nombre_equipo = django_filters.CharFilter(field_name='nombre_equipo', lookup_expr='icontains', label='Nombre del equipo')
    marca = django_filters.CharFilter(field_name='marca', lookup_expr='icontains', label='Marca del equipo')
    modelo = django_filters.CharFilter(field_name='modelo', lookup_expr='icontains', label='Modelo del equipo')
    numero_serie = django_filters.CharFilter(field_name='numero_serie', lookup_expr='icontains', label='Numero de serie del equipo')
    
    class Meta:
        model = models.Equipo_medico
        fields = ['marca', 'modelo', 'numero_serie', 'estado', 'nombre_equipo', 'numero_nacional_inv', 'cama']