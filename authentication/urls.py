from django.urls import path
from .views import *

urlpatterns = [
    path("", RegisterView.as_view(), name="signup"),
    path("signup/", RegisterView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
]
