from typing import Any
from django.shortcuts import get_object_or_404
from inventario.models import Proveedor, Contrato, Equipo_medico
from django.http import HttpResponse
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProveedorSerializers, ContratoSerializers, Equipo_Serializer
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

class ProveedorViewSet(ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializers
    lookup_field = 'id'

    def get_serializer_context(self):
        return {'request': self.request}


class ContratoViewSet(ModelViewSet):
    queryset = Contrato.objects.select_related('proveedor').all()
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
