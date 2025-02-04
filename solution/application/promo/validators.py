from django.core.exceptions import ValidationError

def categories_validator(value):
    if len(value) > 20:
        raise ValidationError('Слишком много категорий')
    if len(min(value, key=len)) < 2:
        raise ValidationError('Слишком короткие категории')
    if len(max(value, key=len)) > 20:
        raise ValidationError('Слишком длинные категории')

def unique_validator(value):
    if len(value) < 1 or len(value) > 5000:
        raise ValidationError('Недопустимое количество элементов')
    if len(min(value, key=len)) < 3:
        raise ValidationError('Слишком короткий промокод')
    if len(max(value, key=len)) > 30:
        raise ValidationError('Слишком длинный промокод')