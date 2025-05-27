from rest_framework import serializers
from .models import *
from authentication.models import User

class PostSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.name", read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    image_url = serializers.CharField(required=False, allow_null=True)
    audio_url = serializers.URLField(required=False, allow_blank=True)
    file_url = serializers.URLField(required=False, allow_blank=True)
    post_type = serializers.ChoiceField(choices=Post.POST_TYPE_CHOICES, default="question")

    class Meta:
        model = Post
        fields = [
            "id", "title", "user", "user_name", "text",
            "image_url", "audio_url", "file_url",
            "created_at", "likes_count", "comments_count", "post_type", "severity_score"
        ]

    def update(self, instance, validated_data):
        image_url = validated_data.pop('image_url', None)
        if image_url is not None:
            validated_data['image'] = image_url
        return super().update(instance, validated_data)

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()


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
        fields = ['id', 'post', 'reported_by', 'reason', 'created_at', 'status', 'is_banned']

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
