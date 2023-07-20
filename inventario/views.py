from typing import Any
from django.shortcuts import get_object_or_404
from inventario.models import Proveedor, Contrato, Equipo_medico, Area_hospital
from django.http import HttpResponse
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProveedorSerializers, ContratoSerializers, Equipo_Serializer, AreaSerializer
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

class ProveedorViewSet(ModelViewSet):
    queryset = Proveedor.objects.prefetch_related('proveedor_contrato').all()
    serializer_class = ProveedorSerializers
    lookup_field = 'id'

class ContratoViewSet(ModelViewSet):
    queryset = Contrato.objects.select_related('proveedor').prefetch_related('equipos_contrato','equipos_contrato__area').all()
    serializer_class = ContratoSerializers
    lookup_field = 'num_contrato'

    def get_serializer_context(self):
        return {'request': self.request}

class EquipoViewSet(ModelViewSet):
    queryset = Equipo_medico.objects.select_related('contrato','area','cama').all()
    serializer_class = Equipo_Serializer
    lookup_field = 'numero_nacional_inv'

    def get_serializer_context(self):
        return {'request': self.request}

class AreaViewSet(ModelViewSet):
    queryset = Area_hospital.objects.prefetch_related('equipos_area').all()
    serializer_class = AreaSerializer
    lookup_field = 'id'
