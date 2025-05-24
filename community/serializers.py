from rest_framework import serializers
from .models import *
from authentication.models import User

class PostSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.name", read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False, allow_null=True)
    audio = serializers.FileField(required=False, allow_null=True)
    file = serializers.FileField(required=False, allow_null=True)
    post_type = serializers.ChoiceField(choices=Post.POST_TYPE_CHOICES, default="question")

    class Meta:
        model = Post
        fields = ["id", "user", "user_name", "text", "image", "audio", "file", "created_at", "likes_count", "comments_count", "post_type"]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_image_url(self, obj):
        # Since Cloudinary URLs are absolute, return directly
        if obj.image:
            return obj.image.url
        return None

    def get_audio_url(self, obj):
        # Provide full URL for audio file
        if obj.audio:
            return obj.audio.url
        return None


class CommunityGuidelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityGuideline
        fields = ['code', 'title', 'description']


class PostReportSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
    reported_by = serializers.PrimaryKeyRelatedField(read_only=True)
    reason = serializers.ChoiceField(choices=PostReport.REASON_CHOICES, required=False, allow_blank=True)
    reason_detail = serializers.SerializerMethodField()

    class Meta:
        model = PostReport
        fields = ["id", "post", "reported_by", "reason", "reason_detail", "created_at", "status"]
        read_only_fields = ["created_at", "status"]

    def get_reason_detail(self, obj):
        try:
            guideline = CommunityGuideline.objects.get(code=obj.reason)
            return CommunityGuidelineSerializer(guideline).data
        except CommunityGuideline.DoesNotExist:
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
