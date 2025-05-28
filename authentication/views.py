from rest_framework.generics import GenericAPIView, CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
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
            tokens = RefreshToken.for_user(user)
            return Response({
                "user": UserSerializer(user).data,
                "access_token": str(tokens.access_token),
                "refresh_token": str(tokens)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Login request data: {request.data}")

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Login serializer errors: {serializer.errors}")
        try:
            if serializer.is_valid(raise_exception=True):
                user = serializer.validated_data["user"]
                tokens = RefreshToken.for_user(user)
                return Response({
                    "user": UserSerializer(user).data,
                    "access_token": str(tokens.access_token),
                    "refresh_token": str(tokens)
                })
        except Exception as e:
            logger.error(f"Login exception: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
from django.db.models import Avg
from .models import Feedback

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

class AverageRatingView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        average_rating = Feedback.objects.aggregate(avg_rating=Avg('rating'))['avg_rating']
        if average_rating is None:
            average_rating = 0
        return Response({"average_rating": round(average_rating, 2)}, status=status.HTTP_200_OK)

class UserVerificationStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        latest_request = VerificationRequest.objects.filter(user=user).order_by('-created_at').first()

        if latest_request:
            if latest_request.is_approved:
                status_str = "approved"
            elif latest_request.is_rejected:
                status_str = "rejected"
            else:
                status_str = "pending"
            rejection_reason = latest_request.rejection_reason if latest_request.is_rejected else None
        else:
            status_str = "no_request"
            rejection_reason = None

        data = {
            "is_verified_researcher": user.is_verified_researcher,
            "is_verified_expert": user.is_verified_expert,
            "verification_request_status": status_str,
            "rejection_reason": rejection_reason,
        }
        return Response(data, status=status.HTTP_200_OK)
    
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
        # Allow submission only if no pending request or last request was rejected
        existing_request = VerificationRequest.objects.filter(user=self.request.user, is_approved=False).order_by('-created_at').first()
        if existing_request and not existing_request.is_rejected:
            raise serializers.ValidationError("You already have a pending verification request.")
        serializer.save(user=self.request.user)

class VerificationRequestListView(ListAPIView):
    queryset = VerificationRequest.objects.select_related('user').filter(is_rejected=False)
    serializer_class = VerificationRequestSerializer
    permission_classes = [IsAdminUser]

class ApproveVerificationView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        from notifications.models import Notification
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

        # Create notification for user
        Notification.objects.create(
            sender=request.user,
            receiver=req.user,
            notification_type="verification",
        )
        # Send push notification
        if req.user.device_token:
            title = "Verification Approved"
            body = "Your verification request has been approved."
            send_push_notification(req.user.device_token, title, body)

        return Response({'detail': 'User verified successfully.'})

class RejectVerificationView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        from notifications.models import Notification
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

        # Create notification for user
        Notification.objects.create(
            sender=request.user,
            receiver=req.user,
            notification_type="verification",
        )
        # Send push notification
        if req.user.device_token:
            title = "Verification Rejected"
            body = "Your verification request has been rejected."
            send_push_notification(req.user.device_token, title, body)

        return Response({"detail": "Verification request rejected."}, status=status.HTTP_200_OK)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
        except KeyError:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
        except (TokenError, InvalidToken) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SubmitFeedbackView(CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
class AdminFeedbackListView(ListAPIView):
    queryset = Feedback.objects.select_related('user').all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAdminUser]
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['user__name', 'user__email', 'comments']
    filterset_fields = ['rating', 'ai_detection_accuracy']

class AdminDeleteUserView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            if user.role == "admin":
                return Response({"error": "Cannot delete an admin user."}, status=status.HTTP_403_FORBIDDEN)
            user.delete()
            return Response({"detail": "User deleted successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
