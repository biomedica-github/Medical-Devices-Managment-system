from django.urls import path, re_path, include
from . import views
from rest_framework.routers import SimpleRouter, DefaultRouter

router = DefaultRouter()
router.register(r'general',views.VerReportesViewSet, 'general')
router.register(r'atendidos', views.VerReportesCompletadosViewSet, basename='atendidos')
router.register(r'pendientes', views.VerReportesPendientesViewSet, basename='pendientes')


# URLConf

urlpatterns = router.urls