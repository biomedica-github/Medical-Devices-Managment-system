from django.urls import path, re_path
from . import views
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('', views.AgendaAdminViewset, basename= 'Agenda')


urlpatterns = router.urls
