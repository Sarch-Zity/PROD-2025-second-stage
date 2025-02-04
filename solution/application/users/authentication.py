from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.cache import cache
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.response import Response
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from functools import wraps

class CustomJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        validated_token = super().get_validated_token(raw_token)
        if cache.get(f"{validated_token.get("userid")}") != validated_token["jti"]:
            raise InvalidToken("Этот токен был отозван.")
        return validated_token

class MyPBKDF2PasswordHasher(PBKDF2PasswordHasher):
    iterations = 100000 

def is_business(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_business:
            return Response({"status": "error", "message": "Пользователь не авторизован."}, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def is_customer(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_business:
            return Response({"status": "error", "message": "Пользователь не авторизован."}, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped_view