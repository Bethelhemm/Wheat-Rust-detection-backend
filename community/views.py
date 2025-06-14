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

# Existing views omitted for brevity...

# Admin views to be added:

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
