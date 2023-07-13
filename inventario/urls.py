from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('listado/', views.listado_proveedores)
]
