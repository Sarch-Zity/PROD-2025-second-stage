from rest_framework import serializers
from .models import CustomUser, Business, Customer, CustomerTarget
from django.core.validators import MinLengthValidator, MaxLengthValidator, MinValueValidator, MaxValueValidator
from .validators import password_validator

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["password"]

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ["name", "email"]

class CustomerSerializer(serializers.ModelSerializer):
    other = serializers.JSONField()
    class Meta:
        model = Customer
        fields = ["name", "surname", "email", "avatar_url", "other"]

class CustomerTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerTarget
        fields = ["age", "country"]

class ProfileCustomerSerializer(serializers.ModelSerializer):
    other = serializers.SerializerMethodField()
    class Meta:
        model = Customer
        fields = ["name", "surname", "email", "avatar_url", "other"]

    def get_other(self, obj):
        other = {}
        other["age"] = obj.customertarget.age
        other["country"] = obj.customertarget.country
        return other

class PachProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, validators=[MinLengthValidator(1), MaxLengthValidator(100)])
    surname = serializers.CharField(required=False, validators=[MinLengthValidator(1), MaxLengthValidator(120)])
    class Meta:
        model = Customer
        fields = ["name", "surname", "avatar_url"]

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[MinLengthValidator(8), MaxLengthValidator(128)])
    password = serializers.CharField(validators=[MinLengthValidator(8), password_validator, MaxLengthValidator(60)])
    class Meta:
        fields = ["email", "password"]