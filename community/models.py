from django.db import models
from authentication.models import User
class Post(models.Model):
    POST_TYPE_CHOICES = [
        ("question", "Question"),
        ("article", "Article"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, default="question")
    text = models.TextField(blank=True, null=True)
import datetime

class Post(models.Model):
    POST_TYPE_CHOICES = [
        ("question", "Question"),
        ("article", "Article"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, default="question")
    text = models.TextField(blank=True, null=True)

    def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<year>/<month>/<filename>
        return 'user_{0}/{1}/{2}/{3}'.format(instance.user.id, datetime.datetime.now().year, datetime.datetime.now().month, filename)

    image = models.URLField(blank=True, null=True)
    audio = models.FileField(upload_to=user_directory_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.user.name}"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.user.name}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.name} on {self.post}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")


class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="saved_posts")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")
