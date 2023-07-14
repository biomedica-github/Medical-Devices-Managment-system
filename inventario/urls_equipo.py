from django.urls import path, re_path
from . import views

# URLConf
urlpatterns = [
    path('', views.listado_equipos),
    re_path('(?P<numero_nacional_inv>\d+)/$', views.equipo_especifico)
]
