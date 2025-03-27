from django.urls import path
from .views import (
    PostCreateView,
    PostListView,
    CommentCreateView,
    LikePostView,
    SavePostView,
)

urlpatterns = [
    path("posts/", PostListView.as_view(), name="post-list"),
    path("posts/create/", PostCreateView.as_view(), name="post-create"),
    path("posts/<int:post_id>/comment/", CommentCreateView.as_view(), name="comment-create"),
    path("posts/<int:post_id>/like/", LikePostView.as_view(), name="like-post"),
    path("posts/<int:post_id>/save/", SavePostView.as_view(), name="save-post"),
]