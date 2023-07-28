from django.urls import path, re_path
from . import views
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('', views.AreaViewSet)

area_router = routers.NestedDefaultRouter(router, '', lookup='id')
area_router.register('equipos_area', views.AreaEquipoViewSet, basename='area-equipo')

servicio_router = routers.NestedDefaultRouter(area_router, 'equipos_area', lookup='equipo')
servicio_router.register('servicio', views.AreaOrdenesViewset, basename='equipo-servicio')



# URLConf
urlpatterns = router.urls  + servicio_router.urls + area_router.urls