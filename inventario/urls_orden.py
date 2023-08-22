from django.urls import path, re_path
from . import views
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('general', views.CrearOrdenViewSet, basename= 'orden')
router.register('servicios_pendientes', views.OrdenPendientesViewSet, basename='orden_pendiente')



# URLConf
urlpatterns = router.urls