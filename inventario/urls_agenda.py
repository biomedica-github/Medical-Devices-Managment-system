from django.urls import path, re_path
from . import views
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers
from django.views.generic import TemplateView

router = routers.DefaultRouter()
router.register("general", views.AgendaAdminViewset, basename="agenda_urls")
router.register("contratos", views.AgendaContratosViewset, basename="vencimiento_urls")

urlpatterns = router.urls + [
    path(
        "seleccion",
        TemplateView.as_view(
            template_name="interfaz/Agenda/agenda-seleccion.html",
        ),
        name="seleccion",
    )
]
