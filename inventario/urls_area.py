from django.urls import path, re_path
from . import views
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('', views.AreaViewSet, basename= 'Area')



#area_router = routers.NestedDefaultRouter(router, '', lookup='id')
#area_router.register('equipos_area', views.AreaEquipoViewSet, basename='area-equipo')

# URLConf
urlpatterns = router.urls 