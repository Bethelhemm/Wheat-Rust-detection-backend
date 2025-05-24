from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

User = get_user_model()

class BannedUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        if user.is_banned:
            raise PermissionDenied("Your account has been banned and you cannot log in.")

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
