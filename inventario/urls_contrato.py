from django.urls import path, re_path
from . import views

# URLConf
urlpatterns = [
    path('', views.listado_contratos),
    re_path('(?P<num_contrato>.*)/$', views.contrato_especifico)
]
