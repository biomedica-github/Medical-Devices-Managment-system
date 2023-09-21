from django.urls import path, re_path
from . import views
from rest_framework.routers import SimpleRouter, DefaultRouter

router = DefaultRouter()
router.register('', views.ProveedorViewSet, basename='proveedorurls')


# URLConf
urlpatterns = router.urls