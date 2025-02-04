from django.db import models
from promo.models import Promo
from users.models import CustomUser
from uuid import uuid4
from django.core.validators import MinLengthValidator

# Create your models here.

class Comment(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False, blank=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="comments")
    promo = models.ForeignKey(Promo, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(max_length=1000, validators=[MinLengthValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True)