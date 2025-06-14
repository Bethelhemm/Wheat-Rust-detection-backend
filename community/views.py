from rest_framework import generics, status, parsers
from rest_framework.permissions import IsAuthenticated, BasePermission, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import exception_handler, APIView
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import PostSerializer, CommentSerializer, LikeSerializer, SavedPostSerializer, PostReportSerializer, CommunityGuidelineSerializer
from notifications.models import Notification

class CustomIsAdminUser(IsAdminUser):
    """
    Custom permission class that returns 403 Forbidden JSON response instead of redirect for unauthorized users.
    """
    def has_permission(self, request, view):
        is_admin = super().has_permission(request, view)
        if not is_admin:
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

class ReportPostView(generics.CreateAPIView):
    serializer_class = PostReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)

class AdminPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Post.objects.all().order_by("-created_at")

class CommunityGuidelineListView(generics.ListAPIView):
    serializer_class = CommunityGuidelineSerializer
    queryset = CommunityGuideline.objects.all()

# Admin views added:

class AdminReportedPostsView(generics.ListAPIView):
    serializer_class = PostReportSerializer
    permission_classes = [CustomIsAdminUser]

    def get_queryset(self):
        return PostReport.objects.all().order_by("-created_at")

class AdminBanPostView(APIView):
    permission_classes = [CustomIsAdminUser]

    def post(self, request, post_id):
        post_report = get_object_or_404(PostReport, post_id=post_id)
        post_report.is_banned = True
        post_report.status = "banned"
        post_report.save()
        return Response({"message": "Post banned successfully."}, status=status.HTTP_200_OK)

class AdminReinstatePostView(APIView):
    permission_classes = [CustomIsAdminUser]

    def post(self, request, post_id):
        post_report = get_object_or_404(PostReport, post_id=post_id)
        post_report.is_banned = False
        post_report.status = "reviewed"
        post_report.save()
        return Response({"message": "Post reinstated successfully."}, status=status.HTTP_200_OK)

class AdminDeleteUserView(APIView):
    permission_classes = [CustomIsAdminUser]

    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return Response({"message": "User deleted successfully."}, status=status.HTTP_200_OK)
