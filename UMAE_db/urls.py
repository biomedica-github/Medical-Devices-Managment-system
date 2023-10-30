"""
URL configuration for UMAE_db project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.views.generic import TemplateView
urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "proveedores/",
        include(
            ("inventario.urls_proveedor", "inventario"), namespace="proveedornamespace"
        ),
    ),
    path("__debug__/", include("debug_toolbar.urls")),
    path("auth/", include("djoser.urls")),
    path(
        "contratos/",
        include(
            ("inventario.urls_contrato", "inventario"), namespace="contratonamespace"
        ),
    ),
    path(
        "equipo_medico/",
        include(("inventario.urls_equipo", "inventario"), namespace="equiponamespace"),
    ),
    path(
        "area/",
        include(("inventario.urls_area", "inventario"), namespace="areanamespace"),
    ),
    path(
        "orden/",
        include(("inventario.urls_orden", "inventario"), namespace="ordennamespace"),
    ),
    path(
        "agenda/",
        include(("inventario.urls_agenda", "inventario"), namespace="agendanamespace"),
    ),
    path(
        "checklists/",
        include(
            ("inventario.urls_checklist", "inventario"), namespace="checklistnamespace"
        ),
    ),
    path(
        "reportes/",
        include(
            ("inventario.urls_reportes", "inventario"), namespace="reportesnamespace"
        ),
    ),
    path("login/", include(("core.urls", "core"), namespace="authnamespace")),
    path(
        "", RedirectView.as_view(url="/login/", permanent=False), name="root-redirect"
    ),path('dashboard', TemplateView.as_view(template_name='inventario/interfaz/dashboard.html'))] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
