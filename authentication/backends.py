import logging
from django.contrib.auth.backends import ModelBackend
from authentication.models import User

logger = logging.getLogger(__name__)

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        logger.info(f"Authenticating user with username: {username}")
        if username is None:
            return None 
        try:
            if '@' in username:
                user = User.objects.get(email=username)
            else:
                user = User.objects.get(phone=username)
        except User.DoesNotExist:
            logger.warning(f"User not found for username: {username}")
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            logger.info(f"User authenticated successfully: {username}")
            return user
        logger.warning(f"Authentication failed for user: {username}")
        return None
