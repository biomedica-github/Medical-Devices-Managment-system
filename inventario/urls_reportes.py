from django.urls import path, re_path, include
from . import views
from rest_framework.routers import SimpleRouter, DefaultRouter

router = DefaultRouter()
router.register(r'cerrados',views.VerReportesCerradosViewSet, 'cerrados')
router.register(r'atendidos', views.VerReportesCompletadosViewSet, basename='atendidos')
router.register(r'pendientes', views.VerReportesPendientesViewSet, basename='pendientes')
router.register(r'seleccion', views.VerSeleccionReportesViewSet, basename='seleccion')


# URLConf

urlpatterns = router.urls