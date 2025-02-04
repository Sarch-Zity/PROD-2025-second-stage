from rest_framework import serializers
from .models import Comment
from django.core.validators import MinValueValidator

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["text"]

class CommentListSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid")
    # date = serializers.DateTimeField(source="created_at", format="%Y-%m-%dT%H:%M:%S%z")
    date = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ["id", "text", "date", "author"]

    def get_author(self, obj):
        output = {"name": obj.user.customer.name, "surname": obj.user.customer.surname}
        if obj.user.customer.avatar_url:
            output["avatar_url"] = obj.user.customer.avatar_url
        return output
    
    def get_date(self, obj):
        output =  obj.created_at.astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
        return output[:-2] + ":" + output[-2:]
    
class PaginatorSerializer(serializers.Serializer):
    offset = serializers.IntegerField(default=0, validators=[MinValueValidator(0)])
    limit = serializers.IntegerField(default=10, validators=[MinValueValidator(0)])