from django.urls import path, re_path
from . import views
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('general', views.EquipoViewSet, basename='equipo_urls')

equipo_router = routers.NestedDefaultRouter(router, 'general', lookup='equipo')
equipo_router.register('servicio', views.OrdenViewSet, basename= 'equipo-orden')
equipo_router.register('agenda', views.AgendaViewSet, basename='equipo-agenda')
equipo_router.register('checklists', views.CheckListEspecificoViewSet, basename='equipo-check')
equipo_router.register('levantar_reporte', views.CrearAtenderReporteViewSet, basename='equipo-reporte')


# URLConf
urlpatterns = router.urls + equipo_router.urls