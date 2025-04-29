from rest_framework.generics import GenericAPIView, CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.db.models import Count
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from django.core.files.uploadedfile import InMemoryUploadedFile
# SupabaseStorage import removed as Supabase storage is no longer used
import os

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
    
class UpdateProfileView(GenericAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request):
        serializer = self.get_serializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            path = default_storage.save(file_obj.name, ContentFile(file_obj.read()))
            file_url = default_storage.url(path)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"file_url": file_url}, status=status.HTTP_201_CREATED)
    
class AdminUserListView(GenericAPIView):
    
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'email', 'phone']
    filterset_fields = ['role']


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
    
class SubmitVerificationRequestView(CreateAPIView):
    queryset = VerificationRequest.objects.all()
    serializer_class = VerificationRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class VerificationRequestListView(ListAPIView):
    queryset = VerificationRequest.objects.select_related('user').all()
    serializer_class = VerificationRequestSerializer
    permission_classes = [IsAdminUser]

class ApproveVerificationView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            req = VerificationRequest.objects.get(pk=pk)
        except VerificationRequest.DoesNotExist:
            return Response({'detail': 'Verification request not found.'}, status=404)

        req.is_approved = True
        req.reviewed_by = request.user
        req.reviewed_at = now()
        req.save()

        # Assign tag to the user
        if req.role == 'researcher':
            req.user.is_verified_researcher = True
        elif req.role == 'expert':
            req.user.is_verified_expert = True
        req.user.save()

        return Response({'detail': 'User verified successfully.'})

class RejectVerificationView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            req = VerificationRequest.objects.get(pk=pk)
        except VerificationRequest.DoesNotExist:
            return Response({"detail": "Verification request not found."}, status=status.HTTP_404_NOT_FOUND)

        if req.is_approved:
            return Response({"detail": "This request is already approved and cannot be rejected."}, status=status.HTTP_400_BAD_REQUEST)

        rejection_reason = request.data.get("reason", "")

        req.is_rejected = True
        req.rejection_reason = rejection_reason
        req.reviewed_by = request.user
        req.reviewed_at = now()
        req.save()

        return Response({"detail": "Verification request rejected."}, status=status.HTTP_200_OK)
    
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