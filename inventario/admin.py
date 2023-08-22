from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from . import models


@admin.register(models.Equipo_medico)
class EquipoMedicoAdmin(admin.ModelAdmin):
    list_display = ['numero_nacional_inv', 'nombre_equipo', 'contrato', 'proveedor']
    list_per_page = 10
    list_select_related = ['contrato', 'area', 'contrato']
    search_fields = ['numero_nacional_inv__istartswith', 'nombre_equipo__istartswith']
    list_filter = ['contrato']

    def proveedor(self, equipo):
        return equipo.contrato.proveedor
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).select_related('contrato__proveedor')

@admin.register(models.Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ['num_contrato', 'proveedor', 'tipo_contrato', 'fecha_vencimiento']
    list_per_page = 10
    list_select_related = ['proveedor']

@admin.register(models.Area_hospital)
class AreaAdmin(admin.ModelAdmin):
    list_display = ['nombre_sala']
    list_per_page = 10

admin.site.register(models.Proveedor)
