from django.contrib.auth.backends import ModelBackend
from authentication.models import User

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            return None 
        try:
            if '@' in username:
                user = User.objects.get(email=username)
            else:
                user = User.objects.get(phone=username)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
