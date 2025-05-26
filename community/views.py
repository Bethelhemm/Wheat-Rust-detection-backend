from rest_framework import generics, status, parsers
from rest_framework.permissions import IsAuthenticated, BasePermission, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from .models import *
from .serializers import PostSerializer, CommentSerializer, LikeSerializer, SavedPostSerializer, PostReportSerializer, CommunityGuidelineSerializer
from notifications.models import Notification
from django.shortcuts import get_object_or_404

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
        return Post.objects.filter(savedpost__user=self.request.user).distinct().order_by('-created_at')

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
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return PostReport.objects.filter(status="pending").order_by("-created_at")

class AdminBanPostView(generics.UpdateAPIView):
    serializer_class = PostReportSerializer
    permission_classes = [IsAdminUser]
    queryset = PostReport.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        post_owner = instance.post.user

        # Avoid banning if already banned
        if instance.status == "banned":
            return Response({"detail": "Post is already banned."}, status=status.HTTP_400_BAD_REQUEST)

        # Increase severity score based on unique reporters
        unique_reporters_count = PostReport.objects.filter(post=instance.post).values('reported_by').distinct().count()
        instance.severity_score = unique_reporters_count
        instance.save()

        # Increment warnings count
        post_owner.warnings_count += 1

        # Send warning notification to post owner before banning
        Notification.objects.create(
            sender=request.user,
            receiver=post_owner,
            notification_type="warning",
            post=instance.post,
            message="Your post has been banned because it violates our community guidelines based on received reports."
        )

        # Delete the post after banning
        instance.post.delete()

        # Temporarily ban user if warnings reach 3
        if post_owner.warnings_count >= 3:
            post_owner.is_banned = True
            post_owner.warnings_count = 0  # reset warnings after ban
            # Send push notification for ban
            if post_owner.device_token:
                from notifications.utils import send_push_notification
                send_push_notification(
                    token=post_owner.device_token,
                    title="Account Banned",
                    body="Your account has been temporarily banned due to multiple violations."
                )
        post_owner.save()

        # Update status to banned
        instance.status = "banned"
        instance.save()

        return Response({"detail": "Post owner has been warned, severity updated, and banned if warnings reached 3."}, status=status.HTTP_200_OK)

class AdminDeleteUserView(generics.DestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = PostReport.objects.all()

    def delete(self, request, *args, **kwargs):
        report = self.get_object()
        user_to_delete = report.post.user
        user_to_delete.delete()
        return Response({"detail": "User account deleted."}, status=status.HTTP_204_NO_CONTENT)

class AdminPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Post.objects.all().order_by("-created_at")

class AdminReinstatePostView(generics.UpdateAPIView):
    serializer_class = PostReportSerializer
    permission_classes = [IsAdminUser]
    queryset = PostReport.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        post_owner = instance.post.user
        # Send warning notification to post owner about reinstatement
        Notification.objects.create(
            sender=request.user,
            receiver=post_owner,
            notification_type="warning",
            post=instance.post,
            message="Your post has been banned because it violates our community guidelines based on received reports."
        )
        # Update status to active
        instance.status = "active"
        instance.save()
        return Response({"detail": "Post has been reinstated and user notified."}, status=status.HTTP_200_OK)

class CommunityGuidelineListView(generics.ListAPIView):
    serializer_class = CommunityGuidelineSerializer
    queryset = CommunityGuideline.objects.all()