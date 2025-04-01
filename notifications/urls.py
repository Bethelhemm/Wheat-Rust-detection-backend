from django.urls import path
from .views import NotificationListView, MarkNotificationAsReadView

urlpatterns = [
    path("notifications/", NotificationListView.as_view(), name="notification-list"),
    path("notifications/<int:pk>/read/", MarkNotificationAsReadView.as_view(), name="notification-read"),
]