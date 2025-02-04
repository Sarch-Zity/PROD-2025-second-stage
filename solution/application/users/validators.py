import re
from django.core.exceptions import ValidationError

def password_validator(value):
    if not re.search(r'[A-Z]', value):
        raise ValidationError(('Должен содержать заглавные символы'))
    if not re.search(r'[a-z]', value):
        raise ValidationError(('Должен содержать строчные символы'))
    if not re.search(r'\d', value):
        raise ValidationError(('Должен содержать цифры'))
    if not re.search(r'[@$!%*?&]', value):
        raise ValidationError(('Пароль должен содержать спец. символы @$!%*?&'))
    # for i in "@$!%*?&":
    #     if i in value: break
    # else:
    #     raise ValidationError(
    #         _('Должен содержать спец символы')
    #     )