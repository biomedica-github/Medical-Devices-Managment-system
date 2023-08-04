from django.urls import path, re_path
from . import views
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('general', views.AreaViewSet, basename= 'Area')

nested_router = routers.NestedDefaultRouter(router, 'general', lookup='id')
nested_router.register('camas', views.CamaViewSet, basename='cama-area')
nested_router.register('agenda', views.AgendaUsuarioViewSet, basename='agenda_usuario')
nested_router.register('equipos_area', views.AreaEquipoViewSet, basename='area-equipo')

checklist_router = routers.NestedDefaultRouter(nested_router, 'equipos_area', lookup = 'area_equipo')
checklist_router.register('checklist', views.CheckListCrearViewSet, basename='checklist_area')
checklist_router.register('levantar_reporte', views.CrearReporteViewSet, basename='reporte_area')



# URLConf
urlpatterns = router.urls + nested_router.urls + checklist_router.urls