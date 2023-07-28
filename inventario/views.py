from typing import Any
from django.shortcuts import get_object_or_404
from inventario.models import Proveedor, Contrato, Equipo_medico, Area_hospital, Orden_Servicio
from django.http import HttpResponse
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProveedorSerializers, ContratoSerializers, Equipo_Serializer, AreaSerializer, OrdenEquipoSerializer, OrdenAgendaSerializer, AgregarEquipoAreaSerializer
from . import serializers
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins
from django.db.models import Q

class ProveedorViewSet(ModelViewSet):
    queryset = Proveedor.objects.prefetch_related('proveedor_contrato').all()
    serializer_class = ProveedorSerializers
    lookup_field = 'id'

class ContratoViewSet(ModelViewSet):
    queryset = Contrato.objects.select_related('proveedor').prefetch_related('equipos_contrato','equipos_contrato__area').all()
    serializer_class = ContratoSerializers

    def get_serializer_context(self):
        return {'request': self.request}

class EquipoViewSet(ModelViewSet):
    queryset = Equipo_medico.objects.select_related('contrato','area','cama').all()
    serializer_class = Equipo_Serializer

    def get_serializer_context(self):
        return {'request': self.request}

class AreaViewSet(ModelViewSet):

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return AgregarEquipoAreaSerializer
        return AreaSerializer
    
    queryset = Area_hospital.objects.prefetch_related('equipos_area').all()
    lookup_field = 'id'
    
class CrearOrdenViewSet(ModelViewSet):
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.CrearOrdenSerializer
        return OrdenEquipoSerializer
    queryset = Orden_Servicio.objects.prefetch_related('equipo_medico').all()

class AreaEquipoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    
    def get_serializer_class(self):
        return serializers.AreaEquipoSerializer
    
    def get_queryset(self):
        print(self.kwargs)
        return Equipo_medico.objects.select_related('area').filter(area=self.kwargs['id_id'])

class AreaOrdenesViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    serializer_class = OrdenEquipoSerializer
    
    def get_queryset(self):
        queryset = Orden_Servicio.objects.prefetch_related('equipo_medico').filter(equipo_medico__numero_nacional_inv=self.kwargs['equipo_pk'])
        return queryset


class OrdenViewSet(ModelViewSet):
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.AgregarServicioEquipo
        return OrdenEquipoSerializer
    
    def get_queryset(self):
        queryset = Orden_Servicio.objects.prefetch_related('equipo_medico').filter(equipo_medico__numero_nacional_inv=self.kwargs['equipo_pk'])
        return queryset
    
    def get_serializer_context(self):
        return {'equipo': self.kwargs['equipo_pk']}

class AgendaViewSet(ModelViewSet):
    serializer_class = OrdenAgendaSerializer
    
    def get_queryset(self):
        return Orden_Servicio.objects.filter(tipo_orden='A', equipo_medico__numero_nacional_inv = self.kwargs['equipo_pk'])

    def get_serializer_context(self):
        return {'equipo': self.kwargs['equipo_pk']}
