
from typing import Any


class CustomHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.COOKIES.get('Token')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        
        response = self.get_response(request)

        return response