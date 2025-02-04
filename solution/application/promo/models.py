from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from .validators import categories_validator, unique_validator
from uuid import uuid4
from users.models import CustomUser

# Create your models here.
class Promo(models.Model):
    promo_id = models.UUIDField(primary_key=True, default=uuid4, editable=False, blank=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="created_promos")
    # target = models.OneToOneField(Target, on_delete=models.CASCADE)
    mode = models.CharField(choices={"COMMON": "COMMON", "UNIQUE":"UNIQUE"})
    description = models.TextField(max_length=300, validators=[MinLengthValidator(10)])
    image_url = models.URLField(max_length=350, blank=True, null=True)
    max_count = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100000000)])
    active_from = models.DateField(blank=True, null=True)
    active_until = models.DateField(blank=True, null=True)
    promo_common = models.CharField(max_length=30, validators=[MinLengthValidator(5)], blank=True, null=True)
    promo_unique = models.JSONField(validators=[unique_validator], blank=True, null=True)
    available_promo_unique = models.JSONField(validators=[unique_validator], blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    like_count = models.ManyToManyField(CustomUser, related_name="liked_promos")
    used_count = models.JSONField(default=list)
    statistic = models.JSONField(default=list)
    
class Target(models.Model):
    promo = models.OneToOneField(Promo, on_delete=models.CASCADE)
    age_from = models.SmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], blank=True, null=True)
    age_until = models.SmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], blank=True, null=True)
    country = models.CharField(max_length=2, validators=[MinLengthValidator(2)], blank=True, null=True)
    categories = models.JSONField(validators=[categories_validator], blank=True, null=True)