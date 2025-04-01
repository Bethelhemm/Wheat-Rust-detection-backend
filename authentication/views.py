from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.db.models import Count
from django.core.mail import send_mail
from django.conf import settings

class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            tokens = RefreshToken.for_user(user)
            return Response({
                "user": UserSerializer(user).data,
                "access_token": str(tokens.access_token),
                "refresh_token": str(tokens)
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AdminUserListView(GenericAPIView):
    """
    API endpoint to retrieve all users. Only accessible by admins.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserStatsView(APIView):
    """
    API endpoint to retrieve user statistics: 
    Total users and count of each role (farmer, researcher, expert).
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_users = User.objects.count()
        role_counts = User.objects.values("role").annotate(count=Count("role"))

        role_data = {role["role"]: role["count"] for role in role_counts}

        return Response(
            {
                "total_users": total_users,
                "role_counts": role_data
            },
            status=status.HTTP_200_OK
        )
    
class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            phone = serializer.validated_data.get('phone')
            user = None
            
            if email:
                user = User.objects.filter(email=email).first()
            elif phone:
                user = User.objects.filter(phone=phone).first()

            if user:
                user.generate_otp()
                
                # Sending OTP via email
                send_mail(
                    'Your OTP Code',
                    f'Your OTP code is {user.otp}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )

                # Sending OTP via SMS (using a service like Twilio)
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                client.messages.create(
                    body=f'Your OTP code is {user.otp}',
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=user.phone
                )
                
                return Response({"message": "OTP sent!"}, status=status.HTTP_200_OK)

            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetVerifyView(GenericAPIView):
    serializer_class = PasswordResetVerifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            otp = serializer.validated_data["otp"]
            new_password = serializer.validated_data["new_password"]
            user = User.objects.filter(otp=otp, otp_expiry__gt=timezone.now()).first()

            if user:
                user.set_password(new_password)
                user.otp = None  # Clear OTP
                user.otp_expiry = None  # Clear expiry
                user.save()
                return Response({"message": "Password reset successful!"}, status=status.HTTP_200_OK)

            return Response({"message": "Invalid OTP or OTP expired."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)