from django.urls import path
from .views import *

urlpatterns = [
    path("", RegisterView.as_view(), name="signup"),
    path("signup/", RegisterView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("users/", AdminUserListView.as_view(), name="admin-users"),
    path("user-stats/", UserStatsView.as_view(), name="user-stats"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path("password-reset/verify/", PasswordResetVerifyView.as_view(), name="password-reset-verify"),

]
