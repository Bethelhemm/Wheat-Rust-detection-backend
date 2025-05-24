from django.db import models
from authentication.models import User
from community.models import Post, Comment

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ("like", "Like"),
        ("comment", "Comment"),
        ("verification", "Verification"),
        ("warning", "Warning"),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_notifications")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    message = models.TextField(null=True, blank=True)

    def __str__(self):
        if self.message:
            return self.message
        if self.notification_type == "verification":
            return f"{self.sender.name} has {self.notification_type} your account"
        return f"{self.sender.name} {self.notification_type}d your post"
