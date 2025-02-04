from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed

def custom_exception_handler(exc, context):
    # Вызов стандартного обработчика исключений DRF
    response = exception_handler(exc, context)

    if isinstance(exc, AuthenticationFailed):
        # Если токен некорректный или истёк, меняем сообщение
        return Response(
            {"status": "error", "message": "Пользователь не авторизован."},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Если ошибка другого типа, оставляем поведение по умолчанию
    return response