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
from .permissions import IsAdminOrReadOnly
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action

class ProveedorViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Proveedor.objects.prefetch_related('proveedor_contrato').all()
    serializer_class = ProveedorSerializers
    lookup_field = 'id'

class ContratoViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Contrato.objects.select_related('proveedor').prefetch_related('equipos_contrato','equipos_contrato__area').all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return serializers.CrearContratoSerializer
        return ContratoSerializers

    def get_serializer_context(self):
        return {'request': self.request}

class EquipoViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Equipo_medico.objects.select_related('contrato','area','cama').all()
    serializer_class = Equipo_Serializer

    def get_serializer_context(self):
        return {'request': self.request}

class AreaViewSet(ModelViewSet):

    permission_classes = [IsAdminOrReadOnly, IsAuthenticated]
    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return AgregarEquipoAreaSerializer
        return AreaSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminOrReadOnly()]

    def get_queryset(self):
        return Area_hospital.objects.prefetch_related('equipos_area', 'responsable').filter(responsable = self.request.user.id)
    
    @action(detail=False, methods= ['GET'])
    def servicio(self, request):
        orden = Orden_Servicio.objects.prefetch_related('equipo_medico').filter(equipo_medico__area__responsable = request.user.id).exclude(tipo_orden='A').all()
        serializer = OrdenEquipoSerializer(orden, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def agenda(self, request):
        orden = Orden_Servicio.objects.prefetch_related('equipo_medico').filter(equipo_medico__area__responsable = request.user.id, tipo_orden = 'A').all()
        serializer = OrdenAgendaSerializer(orden, many=True)
        return Response(serializer.data)


class CrearOrdenViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return serializers.CrearOrdenSerializer
        return OrdenEquipoSerializer
    queryset = Orden_Servicio.objects.prefetch_related('equipo_medico').all()

class AreaEquipoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    
    def get_serializer_class(self):
        return serializers.AreaEquipoSerializer
    
    def get_queryset(self):
        return Equipo_medico.objects.select_related('area').filter(area=self.kwargs['id_id'])

class AreaOrdenesViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    serializer_class = OrdenEquipoSerializer
    
    def get_queryset(self):
        queryset = Orden_Servicio.objects.prefetch_related('equipo_medico').filter(equipo_medico__numero_nacional_inv=self.kwargs['equipo_pk'])
        return queryset


class OrdenViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.AgregarServicioEquipo
        return OrdenEquipoSerializer
    
    def get_queryset(self):
        queryset = Orden_Servicio.objects.prefetch_related('equipo_medico').filter(equipo_medico__numero_nacional_inv=self.kwargs['equipo_pk'])
        return queryset
    
    def get_serializer_context(self):
        return {'equipo': self.kwargs['equipo_pk']}

class AgendaAdminViewset(ModelViewSet):
    serializer_class = serializers.AgendaAdminSerializer
    permission_classes = [IsAdminUser]

    queryset = Orden_Servicio.objects.filter(tipo_orden='A').all()

class AgendaViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = OrdenAgendaSerializer
    
    def get_queryset(self):
        return Orden_Servicio.objects.filter(tipo_orden='A', equipo_medico__numero_nacional_inv = self.kwargs['equipo_pk'])

    def get_serializer_context(self):
        return {'equipo': self.kwargs['equipo_pk']}