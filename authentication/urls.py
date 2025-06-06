from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("", RegisterView.as_view(), name="signup"),
    path("signup/", RegisterView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("profile/update/", UpdateProfileView.as_view(), name="update-profile"),
    path("users/", AdminUserListView.as_view(), name="admin-users"),
    path("user-stats/", UserStatsView.as_view(), name="user-stats"),
    path("verify/request/", SubmitVerificationRequestView.as_view(), name="verify-request"),
    path('review/requests/', VerificationRequestListView.as_view(), name='verify-requests-list'),
    path("verify/approve/<int:pk>/", ApproveVerificationView.as_view(), name="approve-verification"),
    path("verify/reject/<int:pk>/", RejectVerificationView.as_view(), name="reject-verification"),
    path("verification/status/", UserVerificationStatusView.as_view(), name="user-verification-status"),
    path("upload-file/", FileUploadView.as_view(), name="file-upload"),
    path("feedback/submit/", SubmitFeedbackView.as_view(), name="submit-feedback"),
    path("feedback/list/", AdminFeedbackListView.as_view(), name="admin-feedback-list"),
    path("feedback/average-rating/", AverageRatingView.as_view(), name="feedback-average-rating"),
    path('admin/users/<int:user_id>/delete/', AdminDeleteUserView.as_view(), name='admin-delete-user'),

]
