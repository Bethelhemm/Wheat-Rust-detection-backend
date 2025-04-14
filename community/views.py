from rest_framework import generics, status, parsers
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from django.db.models import Q
from .models import Post, Comment, Like, SavedPost
from .serializers import PostSerializer, CommentSerializer, LikeSerializer, SavedPostSerializer
from notifications.models import Notification

class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of a post to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class PostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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

class SavePostView(generics.CreateAPIView):
    serializer_class = SavedPostSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        post_id = self.kwargs.get("post_id")
        post = Post.objects.get(id=post_id)
        saved_post, created = SavedPost.objects.get_or_create(user=request.user, post=post)

        if not created:
            saved_post.delete()
            return Response({"message": "Post removed from saved"}, status=status.HTTP_204_NO_CONTENT)

        return Response({"message": "Post saved"}, status=status.HTTP_201_CREATED)

class PostSearchView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return Post.objects.filter(Q(text__icontains=query)).order_by('-created_at')