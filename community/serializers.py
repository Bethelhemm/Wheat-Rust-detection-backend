from rest_framework import serializers
from .models import *
from authentication.models import User

class PostSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.name", read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False, allow_null=True)
    audio = serializers.FileField(required=False, allow_null=True)
    post_type = serializers.ChoiceField(choices=Post.POST_TYPE_CHOICES, default="question")
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "user", "user_name", "text", "image", "image_url", "audio", "created_at", "likes_count", "comments_count", "post_type"]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.name", read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)  
    class Meta:
        model = Comment
        fields = ["id", "user", "user_name", "post", "text", "created_at"]

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["id", "user", "post", "created_at"]


class SavedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedPost
        fields = ["id", "user", "post", "created_at"]
