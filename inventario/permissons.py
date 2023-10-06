from rest_framework.authentication import SessionAuthentication

class CustomAuth(SessionAuthentication):

    def enforce_csrf(self, request):
        return