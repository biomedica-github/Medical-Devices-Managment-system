from django.core.paginator import Page
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    template = "interfaz/pagination/numbers.html"
