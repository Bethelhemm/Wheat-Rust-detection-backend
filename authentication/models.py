from datetime import timedelta
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import pyotp
import random
from django.utils.timezone import now

class UserManager(BaseUserManager):
    def create_user(self, name, email=None, phone=None, password=None, role="user"):
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
        ("user", "User"),
        ("farmer", "Farmer"),
        ("researcher", "Researcher"),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    otp_secret = models.CharField(max_length=32, default=pyotp.random_base32)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)

    def generate_otp(self):
        otp = f"{random.randint(100000, 999999)}"
        self.otp_code = otp
        self.otp_expiry = now() + timedelta(minutes=5)
        self.save()
        return otp

    def verify_otp(self, otp):
        if self.otp_code == otp and self.otp_expiry > now():
            return True
        return False

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def __str__(self):
        return self.name
