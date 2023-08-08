from rest_framework.test import APIClient
from rest_framework import status


class TestProveedor:
    def test_if_user_is_anon_returns_401_get_operation(self):
    
        client = APIClient()
        respuesta = client.get('/proveedores')

        assert respuesta.status_code == status.HTTP_401_UNAUTHORIZED
        

