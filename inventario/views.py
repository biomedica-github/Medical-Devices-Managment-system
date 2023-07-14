from django.shortcuts import get_object_or_404
from inventario.models import Proveedor, Contrato
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ProveedorSerializers, ContratoSerializers
from rest_framework import status

@api_view()
def listado_proveedores(request):
    lista_proveedores = Proveedor.objects.all()
    serializer = ProveedorSerializers(lista_proveedores, many=True)

    return Response(serializer.data)


@api_view()
def proveedor_especifico(request, id):
    proveedor = get_object_or_404(Proveedor, pk=id)
    serializer = ProveedorSerializers(proveedor)
    return Response(serializer.data)
  
@api_view()
def listado_contratos(request):
    lista_contratos = Contrato.objects.select_related('proveedor').all()
    serializer = ContratoSerializers(lista_contratos, many = True)

    return Response(serializer.data)

@api_view()
def contrato_especifico(request, num_contrato):
    num_contrato = num_contrato[1:]
    contrato = get_object_or_404(Contrato, pk=num_contrato)
    serializer = ContratoSerializers(contrato)
    return Response(serializer.data)