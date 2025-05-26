from django.db import models
from authentication.models import User
import datetime

class Post(models.Model):
    POST_TYPE_CHOICES = [
        ("question", "Question"),
        ("article", "Article"),
    ]
    
    title= models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, default="question")
    text = models.TextField(blank=True, null=True)

    def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<year>/<month>/<filename>
        return 'user_{0}/{1}/{2}/{3}'.format(instance.user.id, datetime.datetime.now().year, datetime.datetime.now().month, filename)

    image = models.URLField(blank=True, null=True)
    audio_url = models.URLField(blank=True, null=True)
    file_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.user.name}"

class PostReport(models.Model):
    REASON_CHOICES = [
        ("inaccurate_diagnosis", "Inaccurate Diagnosis – The post shows incorrect or misleading disease detection."),
        ("offensive_content", "Offensive or Inappropriate Content – The post contains language or images that are not appropriate."),
        ("spam_irrelevant", "Spam or Irrelevant Information – The post is unrelated to wheat rust or is promotional."),
        ("duplicate_post", "Duplicate or Repetitive Post – This content has already been posted."),
        ("misleading_image", "Fake or Misleading Image – The image is edited, not real, or doesn’t match the claim."),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reports")
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_reports")
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="pending")  # pending, reviewed, banned
    severity_score = models.IntegerField(default=0)

    def __str__(self):
        return f"Report on Post {self.post.id} by {self.reported_by.name}"

class CommunityGuideline(models.Model):
    code = models.CharField(max_length=30, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title
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
