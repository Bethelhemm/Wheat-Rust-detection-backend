from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (
    PostCreateView,
    PostListView,
    CommentCreateView,
    LikePostView,
    SavePostView,
    PostSearchView,
    PostUpdateView,  
    PostDeleteView,
    CommentListView,
    ReportPostView,
    AdminReportedPostsView,
    AdminBanPostView,
    AdminDeleteUserView,
    AdminPostsView,
    AdminReinstatePostView,
    CommunityGuidelineListView,
    UserSavedPostsView,
)

urlpatterns = [
    path("posts/", PostListView.as_view(), name="post-list"),
    path("posts/create/", PostCreateView.as_view(), name="post-create"),
    path("posts/<int:post_id>/comment/", CommentCreateView.as_view(), name="comment-create"),
    path("posts/<int:post_id>/like/", LikePostView.as_view(), name="like-post"),
    path("posts/<int:post_id>/save/", SavePostView.as_view(), name="save-post"),
    path("posts/saved/", UserSavedPostsView.as_view(), name="user-saved-posts"),
    path("posts/search/", PostSearchView.as_view(), name="post-search"),
    path("posts/<int:post_id>/comments/", CommentListView.as_view(), name="comment-list"),

    path("posts/<int:pk>/update/", PostUpdateView.as_view(), name="post-update"),
    path("posts/<int:pk>/delete/", PostDeleteView.as_view(), name="post-delete"),

    path("posts/<int:post_id>/report/", ReportPostView.as_view(), name="post-report"),
    path("admin/reported-posts/", AdminReportedPostsView.as_view(), name="admin-reported-posts"),
    path("admin/ban-post/<int:pk>/", AdminBanPostView.as_view(), name="admin-ban-post"),
    path("admin/delete-user/<int:pk>/", AdminDeleteUserView.as_view(), name="admin-delete-user"),
    path("admin/posts/", AdminPostsView.as_view(), name="admin-posts"),
    path("admin/reinstate-post/<int:pk>/", AdminReinstatePostView.as_view(), name="admin-reinstate-post"),
    path("settings/community-guidelines/", CommunityGuidelineListView.as_view(), name="community-guidelines"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)