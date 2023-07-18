from django.urls import path, re_path
from . import views

# URLConf
urlpatterns = [
    path('', views.ListaProveedor.as_view()),
    path('<int:id>/', views.ProveedorEspecifico.as_view())
]
