from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        user_auth_tuple = super().authenticate(request)
        if user_auth_tuple is None:
            return None  
        user, token = user_auth_tuple

        if not isinstance(user, User):
            raise AuthenticationFailed("Invalid user type.")

        if not user.is_active:
            raise AuthenticationFailed("User account is disabled.")

        return user, token
