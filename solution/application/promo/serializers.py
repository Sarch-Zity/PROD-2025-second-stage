from rest_framework import serializers
from .models import Promo, Target
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, MaxLengthValidator
import datetime

class PromoSerializer(serializers.ModelSerializer):
    target = serializers.JSONField()
    class Meta:
        model = Promo
        fields = ["mode", "description", "target", "image_url", "max_count", "active_from", "active_until", "promo_common", "promo_unique"]

class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ["age_from", "age_until", "country", "categories"]

class PromoListSerializer(serializers.ModelSerializer):
    target = serializers.SerializerMethodField()
    company_id = serializers.UUIDField(source="user.business.uuid")
    company_name = serializers.CharField(source="user.business.name")
    like_count = serializers.SerializerMethodField()
    active = serializers.SerializerMethodField()
    used_count = serializers.SerializerMethodField()

    class Meta:
        model = Promo
        fields = ["promo_id", "company_id", "company_name", "like_count", "used_count", "active", "mode", "promo_common", "promo_unique", "description", "image_url", "target", "max_count", "active_from", "active_until"]

    def get_target(self, obj):
        target = dict()
        if obj.target.age_from != None:
            target["age_from"] = obj.target.age_from
        if obj.target.age_until != None:
            target["age_until"] = obj.target.age_until
        if obj.target.country != None:
            target["country"] = obj.target.country
        if obj.target.categories != None:
            target["categories"] = obj.target.categories
        return target
    
    def get_like_count(self, obj):
        return obj.like_count.count()
    
    def get_active(self, obj):
        out = True
        if obj.active_from and obj.active_from > datetime.date.today():
            out = False
        elif obj.active_until and obj.active_until < datetime.date.today():
            out = False
        elif obj.mode == "UNIQUE":
            if len(obj.available_promo_unique) <= 0:
                out = False
        elif obj.mode == "COMMON":
            if len(obj.used_count) >= obj.max_count:
                out = False
        return out
    
    def get_used_count(self, obj):
        return len(obj.used_count)

class UpdatePromoSerializer(serializers.ModelSerializer):
    target = serializers.JSONField(required=False)
    description = serializers.CharField(required=False, validators=[MinLengthValidator(10), MaxLengthValidator(300)])
    max_count = serializers.IntegerField(required=False, validators=[MinValueValidator(0), MaxValueValidator(100000000)])
    # image_url = serializers.IntegerField(required=False, allow_null=True)
    # active_from = serializers.IntegerField(required=False, allow_null=True)
    # active_until = serializers.IntegerField(required=False, allow_null=True)
    class Meta:
        model = Promo
        fields = ["description", "target", "image_url", "max_count", "active_from", "active_until"]

class PaginatorBusinessSerializer(serializers.Serializer):
    offset = serializers.IntegerField(default=0, validators=[MinValueValidator(0)])
    limit = serializers.IntegerField(default=10, validators=[MinValueValidator(0)])
    sort_by = serializers.CharField(default="created_at")

class PaginatorCustomerSerializer(serializers.Serializer):
    offset = serializers.IntegerField(default=0, validators=[MinValueValidator(0)])
    limit = serializers.IntegerField(default=10, validators=[MinValueValidator(0)])
    category = serializers.CharField(required=False, validators=[MinLengthValidator(2), MaxLengthValidator(200)])
    active = serializers.BooleanField(required=False)

class PromoListForCustomerSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(source="user.business.uuid")
    company_name = serializers.CharField(source="user.business.name")
    like_count = serializers.SerializerMethodField()
    is_activated_by_user = serializers.BooleanField(default=False)
    is_liked_by_user = serializers.BooleanField(default=False)
    active = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Promo
        fields = ["promo_id", "company_id", "company_name", "description", "image_url", "active", "is_activated_by_user", "like_count", "is_liked_by_user", "comment_count"]

    def get_like_count(self, obj):
        return obj.like_count.count()
    
    def get_comment_count(self, obj):
        return obj.comments.count()
    
    def get_active(self, obj):
        out = True
        if obj.active_from and obj.active_from > datetime.date.today():
            out = False
        elif obj.active_until and obj.active_until < datetime.date.today():
            out = False
        elif obj.mode == "UNIQUE":
            if len(obj.available_promo_unique) <= 0:
                out = False
        elif obj.mode == "COMMON":
            if len(obj.used_count) >= obj.max_count:
                out = False
        return out
