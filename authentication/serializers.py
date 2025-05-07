from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import *
from django.core.mail import send_mail, BadHeaderError
from django.utils.timezone import now
from django.core.exceptions import ImproperlyConfigured
import logging
logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "name", "email", "phone", "role", "profile_image", "is_active"]

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "name", "email", "phone", "role", "password", "password2", "profile_image"]
    
    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email", "")
        phone = data.get("phone", "")
        password = data.get("password")

        logger.info(f"Login attempt with email: {email}, phone: {phone}, password provided: {'yes' if password else 'no'}")

        if email:
            auth_username = email
        elif phone:
            auth_username = phone
        else:
            logger.warning("Login failed: Email or phone is required.")
            raise serializers.ValidationError("Email or phone is required.")

        user = authenticate(username=auth_username, password=password)

        if user is None:
            logger.warning(f"Login failed for username: {auth_username}")
            raise serializers.ValidationError("Invalid credentials.")

        logger.info(f"Login successful for user id: {user.id}")
        return {"user": user}


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "name", "profile_image"]

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.name = validated_data.get("name", instance.name)
        instance.profile_image = validated_data.get("profile_image", instance.profile_image)
        instance.save()
        return instance

class VerificationRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = VerificationRequest
        fields = [
            'id', 'user_name', 'user_email', 'user_phone',
            'role', 'certificate', 'created_at',
            'is_approved', 'is_rejected', 'rejection_reason'
        ]


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)

    def validate(self, data):
        email = data.get("email")
        phone = data.get("phone")

        if not email and not phone:
            raise serializers.ValidationError("Email or phone is required.")
        
        return data

class PasswordResetVerifySerializer(serializers.Serializer):
    otp = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["new_password2"]:
            raise serializers.ValidationError("Passwords must match.")
        return data
    
