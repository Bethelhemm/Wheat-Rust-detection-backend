from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from django.core.mail import send_mail, BadHeaderError
from django.utils.timezone import now
from django.core.exceptions import ImproperlyConfigured

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "email", "phone", "role"]

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["name", "email", "phone", "role", "password", "password2"]
    
    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = None
        if data.get("email"):
            user = authenticate(email=data["email"], password=data["password"])
        elif data.get("phone"):
            user = authenticate(phone=data["phone"], password=data["password"])
        
        if user is None:
            raise serializers.ValidationError("Invalid credentials.")
        
        return {"user": user}

