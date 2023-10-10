from django.shortcuts import redirect
from django.urls import reverse
from UMAE_db import settings
from rest_framework.views import exception_handler

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Check if the session has expired.
            if not request.session.get_expiry_age():
                # Session has expired; redirect to the login page.
                login_url = settings.LOGOUT_REDIRECT_URL  # Replace 'login' with your actual login URL name
                return redirect(login_url)

        return response

def custom_exception_handler(exc, context):
    # Handle custom logic here
    exception = str(exc)
    response = exception_handler(exc, context)
    print(f'hey{exception} {type(exception)}')
    if exception == 'Authentication credentials were not provided.':
        print('hey')
        # Customize the response for unauthenticated users here
        login_url = settings.LOGOUT_REDIRECT_URL
        return redirect(login_url)
    elif exception == 'You do not have permission to perform this action.':
        return redirect(settings.HOME)
    return response

