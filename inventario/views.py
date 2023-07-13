from django.shortcuts import render
from inventario.models import Proveedor


def listado_proveedores(request):
    lista_proveedores = Proveedor.objects.all()

    return render(request, 'pruebas.html', {'lista de proveedores:': list(lista_proveedores)})
