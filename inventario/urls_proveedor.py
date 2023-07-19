from django.urls import path, re_path
from . import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('', views.ProveedorViewSet)


# URLConf
urlpatterns = router.urls