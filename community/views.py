from rest_framework import generics, status, parsers
from rest_framework.permissions import IsAuthenticated, BasePermission, IsAuthenticatedOrReadOnly, IsAdminUser

# Replace IsAdminUser with CustomIsAdminUser in admin views to avoid redirect on permission failure
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import exception_handler, APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import *
from .serializers import PostSerializer, CommentSerializer, LikeSerializer, SavedPostSerializer, PostReportSerializer, CommunityGuidelineSerializer
from notifications.models import Notification
from django.shortcuts import get_object_or_404

class CustomIsAdminUser(IsAdminUser):
    """
    Custom permission class that returns 403 Forbidden JSON response instead of redirect for unauthorized users.
    """
    def has_permission(self, request, view):
        is_admin = super().has_permission(request, view)
        if not is_admin:
            # Instead of redirect, raise PermissionDenied to return 403 JSON response
            raise PermissionDenied(detail="You do not have permission to perform this action.")
        return True
    
class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of a post to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsVerifiedExpertOrResearcher(BasePermission):
    """
    Custom permission to allow only verified agricultural experts or researchers to create posts.
    """
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (user.is_verified_researcher or user.is_verified_expert)

class PostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def perform_create(self, serializer):
        user = self.request.user
        post_type = serializer.validated_data.get("post_type", "question")
        if post_type == "article":
            if not (user.is_verified_researcher or user.is_verified_expert):
                raise PermissionDenied("Only verified agricultural experts or researchers can post articles.")
        serializer.save(user=user)

class PostListView(generics.ListAPIView):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer

class PostUpdateView(generics.UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

class PostDeleteView(generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

class LikePostView(generics.CreateAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        post_id = self.kwargs.get("post_id")
        post = Post.objects.get(id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if not created:
            like.delete()
            return Response({"message": "Like removed"}, status=status.HTTP_204_NO_CONTENT)

        if post.user != request.user:
            Notification.objects.create(
                sender=request.user,
                receiver=post.user,
                notification_type="like",
                post=post
            )

        return Response({"message": "Post liked"}, status=status.HTTP_201_CREATED)

class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        comment = serializer.save(user=self.request.user)
        if comment.post.user != self.request.user:
            Notification.objects.create(
                sender=self.request.user,
                receiver=comment.post.user,
                notification_type="comment",
                post=comment.post,
                comment=comment
            )

class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post_id=post_id).order_by('-created_at')


class SavePostView(generics.CreateAPIView):
    serializer_class = SavedPostSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        post_id = self.kwargs.get("post_id")
        post = get_object_or_404(Post, id=post_id)

        # Try to get or create the saved post
        saved_post, created = SavedPost.objects.get_or_create(user=request.user, post=post)

        if not created:
            saved_post.delete()
            return Response({"message": "Post unsaved", "saved": False}, status=status.HTTP_200_OK)

        return Response({"message": "Post saved", "saved": True}, status=status.HTTP_201_CREATED)
class UserSavedPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(saved_posts__user=self.request.user).distinct().order_by('-created_at')

class PostSearchView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return Post.objects.filter(Q(text__icontains=query)).order_by('-created_at')

# New views for post reporting and admin management

class ReportPostView(generics.CreateAPIView):
    serializer_class = PostReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)

class AdminReportedPostsView(generics.ListAPIView):
    serializer_class = PostReportSerializer
    permission_classes = [CustomIsAdminUser]

    def get_queryset(self):
        return PostReport.objects.filter(status="pending").order_by("-created_at")

class AdminBanPostView(generics.UpdateAPIView):
    serializer_class = PostReportSerializer
    permission_classes = [CustomIsAdminUser]
    queryset = PostReport.objects.all()

    def perform_update(self, serializer):
        instance = serializer.instance
        post = instance.post

        # Soft ban post
        post.is_banned = True
        post.save()

        # Update all reports for this post
        unique_reporters_count = PostReport.objects.filter(post=post).values('reported_by').distinct().count()
        PostReport.objects.filter(post=post).update(
            is_banned=True,
            severity_score=unique_reporters_count,
            status="banned"
        )

        post_owner = post.user
        post_owner.warnings_count += 1

        # Send warning notification
        Notification.objects.create(
            sender=self.request.user,
            receiver=post_owner,
            notification_type="warning",
            post=post,
            message="Your post has been banned due to multiple violations."
        )

        # Temporary ban if warnings >= 3
        if post_owner.warnings_count >= 3:
            post_owner.is_banned = True
            post_owner.warnings_count = 0
            if post_owner.device_token:
                from notifications.utils import send_push_notification
                send_push_notification(
                    token=post_owner.device_token,
                    title="Account Banned",
                    body="Your account has been temporarily banned due to repeated violations."
                )

        post_owner.save()

class AdminDeleteUserView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            if user.is_superuser or user.role == "admin":
                return Response({"error": "Cannot delete admin/superuser."}, status=status.HTTP_403_FORBIDDEN)
            user.delete()
            return Response({"detail": "User deleted successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

class AdminPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Post.objects.all().order_by("-created_at")

class AdminReinstatePostView(generics.UpdateAPIView):
    serializer_class = PostReportSerializer
    permission_classes = [IsAdminUser]
    queryset = PostReport.objects.all()

    def perform_update(self, serializer):
        instance = serializer.instance
        post = instance.post

        post.is_banned = False
        post.save()

        PostReport.objects.filter(post=post).update(is_banned=False, status="active")

        Notification.objects.create(
            sender=self.request.user,
            receiver=post.user,
            notification_type="info",
            post=post,
            message="Your post has been reinstated after review."
        )

class CommunityGuidelineListView(generics.ListAPIView):
    serializer_class = CommunityGuidelineSerializer
    queryset = CommunityGuideline.objects.all()