from django.urls import path
from .views import NotificationListView, MarkNotificationAsReadView

urlpatterns = [
    path("", NotificationListView.as_view(), name="notification-list"),
    path("<int:pk>/read/", MarkNotificationAsReadView.as_view(), name="notification-read"),
]