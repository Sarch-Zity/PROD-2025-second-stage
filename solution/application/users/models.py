from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import MinLengthValidator, MaxLengthValidator, MinValueValidator, MaxValueValidator
from uuid import uuid4
from .validators import password_validator

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, id, password=None):
        user = self.model(id)
        user.set_password(password)
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    id = models.BigAutoField(auto_created=True, blank=False, primary_key=True)
    password = models.CharField(validators=[MinLengthValidator(8), password_validator, MaxLengthValidator(60)])
    is_business = models.BooleanField(default=False, blank=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'id'

    def __str__(self):
        return str(self.id)

class Business(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False, blank=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, blank=False)
    name = models.CharField(max_length=50, blank=False, validators=[MinLengthValidator(5)])
    email = models.EmailField(max_length=128, blank=False, validators=[MinLengthValidator(8)], unique=True)

class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, blank=False)
    name = models.CharField(max_length=100, blank=False, validators=[MinLengthValidator(1)])
    surname = models.CharField(max_length=120, blank=False, validators=[MinLengthValidator(1)])
    email = models.EmailField(max_length=128, blank=False, validators=[MinLengthValidator(8)], unique=True)
    avatar_url = models.URLField(max_length=350, blank=True, null=True)
    activated_promos = models.JSONField(default=list)

class CustomerTarget(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    age = models.SmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    country = models.CharField(max_length=2, validators=[MinLengthValidator(2)])