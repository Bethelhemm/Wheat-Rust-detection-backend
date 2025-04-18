from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from datetime import timedelta
import random
import string
class UserManager(BaseUserManager):
    def create_user(self, name, email=None, phone=None, password=None, role="farmer"):
        if not email and not phone:
            raise ValueError("Users must have either an email or phone number.")
        user = self.model(name=name, email=email, phone=phone, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, password, phone=None, role="admin"):
        user = self.create_user(name=name, email=email, phone=phone, password=password, role=role)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("farmer", "Farmer"),
        ("researcher", "Agricultural Researcher"),
        ("expert", "Agricultural Expert"),
    ]

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

    def generate_otp(self):
        self.otp = ''.join(random.choices(string.digits, k=6))
        self.otp_expiry = timezone.now() + timedelta(minutes=5)  # OTP valid for 5 minutes
        self.save()

    objects = UserManager()

    USERNAME_FIELD = "email"  # Set email as the unique identifier
    REQUIRED_FIELDS = ["name", "phone"]

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
    is_approved = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    rejection_reason = models.TextField(null=True, blank=True)