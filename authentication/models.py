from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from datetime import timedelta
import random
import string
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from datetime import timedelta
import random
import string

class UserManager(BaseUserManager):
    def create_user(self, email=None, phone=None, username=None, password=None, role= "farmer", **extra_fields):
        if not email and not phone:
            raise ValueError("Users must have either an email or phone number.")
        
        user = self.model(
            email=self.normalize_email(email) if email else None,
            phone=phone,
            username=username,
            **extra_fields
        )
        user.role = role
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, name, email, password, phone=None, role="admin"):
        user = self.create_user(username=username, name=name, email=email, phone=phone, password=password, role=role)
        user.is_staff = True
        user.is_superuser = True
        user.role = role
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("farmer", "Farmer"),
        ("researcher", "Agricultural Researcher"),
        ("expert", "Agricultural Expert"),
    ]

    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="farmer")
    profile_image = models.ImageField(upload_to="profile_images/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified_researcher = models.BooleanField(default=False)
    is_verified_expert = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    device_token = models.CharField(max_length=255, null=True, blank=True)

    def get_username(self):
        # Return email if present, else phone
        if self.email:
            return self.email
        return self.phone

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.email and not self.phone:
            raise ValidationError("User must have either an email or phone number.")


    def generate_otp(self):
        self.otp = ''.join(random.choices(string.digits, k=6))
        self.otp_expiry = timezone.now() + timedelta(minutes=5)  # OTP valid for 5 minutes
        self.save()

    objects = UserManager()

    USERNAME_FIELD = "email"  # Set email as the unique identifier
    REQUIRED_FIELDS = ["username", "name", "phone"]

    def __str__(self):
        return self.name
    
class VerificationRequest(models.Model):
    ROLE_CHOICES = [
        ('researcher', 'Agricultural Researcher'),
        ('expert', 'Agricultural Expert'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    certificate = models.FileField(upload_to='certificates/')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    rejection_reason = models.TextField(null=True, blank=True)

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    RATING_CHOICES = [
        (1, '1 - Very Poor'),
        (2, '2 - Poor'), 
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent')
    ]
    rating = models.IntegerField(choices=RATING_CHOICES)
    comments = models.TextField(blank=True, null=True)
    ai_detection_accuracy = models.BooleanField(
        help_text="Did the AI correctly identify the disease?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback from {self.user.name} - {self.get_rating_display()}"