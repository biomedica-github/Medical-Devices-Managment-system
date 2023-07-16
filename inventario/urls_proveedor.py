from django.urls import path, re_path
from . import views

# URLConf
urlpatterns = [
    path('', views.listado_proveedores),
    path('<int:id>/', views.proveedor_especifico)
]
