from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='core/index.html')),
    path('auth', views.LoginView.as_view()),
]