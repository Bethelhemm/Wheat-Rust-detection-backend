from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import *
from .serializers import *
from django.db.models import Q
class PostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PostListView(generics.ListAPIView):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer

class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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

        return Response({"message": "Post liked"}, status=status.HTTP_201_CREATED)

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