from typing import Any
from django.shortcuts import get_object_or_404
from inventario.models import Proveedor, Contrato, Equipo_medico
from django.http import HttpResponse
from rest_framework.generics import ListCreateAPIView
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProveedorSerializers, ContratoSerializers, Equipo_Serializer
from rest_framework import status

class ListaProveedor(ListCreateAPIView):
    def get_queryset(self):
        return Proveedor.objects.all()
    
    def get_serializer_class(self):
        return ProveedorSerializers
    
    def get_serializer_context(self):
        return {'request': self.request}

class ProveedorEspecifico(APIView):
    def get(self, request, id):
        proveedor = get_object_or_404(Proveedor, pk=id)
        serializer = ProveedorSerializers(proveedor)
        return Response(serializer.data)

    def put(self, request, id):
        proveedor = get_object_or_404(Proveedor, pk=id)
        serializer = ProveedorSerializers(proveedor, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def delete(self, request, id):
        proveedor = get_object_or_404(Proveedor, pk=id)
        proveedor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view()
def listado_contratos(request):
    lista_contratos = Contrato.objects.select_related('proveedor').all()
    serializer = ContratoSerializers(lista_contratos, many = True)

    return Response(serializer.data)

@api_view()
def contrato_especifico(request, num_contrato):
    contrato = get_object_or_404(Contrato, pk=num_contrato)
    serializer = ContratoSerializers(contrato)
    return Response(serializer.data)

@api_view()
def listado_equipos(request):
    lista_equipos = Equipo_medico.objects.select_related('contrato','area','cama').all()
    serializer = Equipo_Serializer(lista_equipos, many=True)

    return Response(serializer.data)

@api_view()
def equipo_especifico(request, numero_nacional_inv):
    equipo = get_object_or_404(Equipo_medico, pk=numero_nacional_inv)
    serializer = Equipo_Serializer(equipo)
    return Response(serializer.data)