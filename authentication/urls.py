from django.urls import path
from .views import *

urlpatterns = [
    path("", RegisterView.as_view(), name="signup"),
    path("signup/", RegisterView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/update/", UpdateProfileView.as_view(), name="update-profile"),
    path("users/", AdminUserListView.as_view(), name="admin-users"),
    path("user-stats/", UserStatsView.as_view(), name="user-stats"),
    path("verify/request/", SubmitVerificationRequestView.as_view(), name="verify-request"),
    path('review/requests/', VerificationRequestListView.as_view(), name='verify-requests-list'),
    path("verify/approve/<int:pk>/", ApproveVerificationView.as_view(), name="approve-verification"),
    path("verify/reject/<int:pk>/", RejectVerificationView.as_view(), name="reject-verification"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path("password-reset/verify/", PasswordResetVerifyView.as_view(), name="password-reset-verify"),

]
