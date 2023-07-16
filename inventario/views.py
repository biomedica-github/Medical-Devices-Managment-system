from django.shortcuts import get_object_or_404
from inventario.models import Proveedor, Contrato, Equipo_medico
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ProveedorSerializers, ContratoSerializers, Equipo_Serializer
from rest_framework import status

@api_view(['GET','POST'])
def listado_proveedores(request):
    if request.method == 'GET':
        lista_proveedores = Proveedor.objects.all()
        serializer = ProveedorSerializers(lista_proveedores, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
         serializer = ProveedorSerializers(data = request.data)
         serializer.is_valid(raise_exception=True)
         print(serializer)

         serializer.save()
         return Response(serializer.data, status= status.HTTP_201_CREATED)


@api_view(['GET','PUT', 'DELETE'])
def proveedor_especifico(request, id):
    proveedor = get_object_or_404(Proveedor, pk=id)
    if request.method == 'GET':
        serializer = ProveedorSerializers(proveedor)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ProveedorSerializers(proveedor, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
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