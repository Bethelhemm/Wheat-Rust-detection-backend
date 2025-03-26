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

class ForgotPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()

    def validate(self, data):
        user = User.objects.filter(email=data["email_or_phone"]).first() or \
               User.objects.filter(phone=data["email_or_phone"]).first()
        
        if not user:
            raise serializers.ValidationError("User not found.")
        
        otp = user.generate_otp()

        if user.email:
            try:
                send_mail(
                    subject="Password Reset OTP",
                    message=f"Your OTP is {otp}",
                    from_email="noreply@example.com",
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except BadHeaderError:
                raise serializers.ValidationError("Invalid email header found.")
            except ImproperlyConfigured as e:
                raise serializers.ValidationError(f"Email configuration error: {str(e)}")
            except Exception as e:
                raise serializers.ValidationError(f"Error sending email: {str(e)}")
        
        return {"message": "OTP sent successfully."}

class VerifyOTPSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()
    otp = serializers.CharField()

    def validate(self, data):
        user = User.objects.filter(email=data["email_or_phone"]).first() or \
               User.objects.filter(phone=data["email_or_phone"]).first()
        
        if not user or not user.verify_otp(data["otp"]):
            raise serializers.ValidationError("Invalid or expired OTP.")
        
        return {"message": "OTP verified successfully."}

class ResetPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()
    new_password = serializers.CharField()
    otp = serializers.CharField()

    def validate(self, data):
        user = User.objects.filter(email=data["email_or_phone"]).first() or \
               User.objects.filter(phone=data["email_or_phone"]).first()
        
        if not user or not user.verify_otp(data["otp"]):
            raise serializers.ValidationError("Invalid OTP.")
        
        user.set_password(data["new_password"])
        user.otp_code = None  # Clear OTP after use
        user.save()
        
        return {"message": "Password reset successful."}
