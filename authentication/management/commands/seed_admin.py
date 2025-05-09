from django.core.management.base import BaseCommand
from authentication.models import User
from decouple import config

class Command(BaseCommand):
    help = "Seed or update the initial admin user"

    def handle(self, *args, **kwargs):
        admin_email = config("ADMIN_EMAIL")
        admin_phone = config("ADMIN_PHONE")
        admin_password = config("ADMIN_PASSWORD")
        admin_username = config("ADMIN_USERNAME", default="admin")

        user, created = User.objects.get_or_create(email=admin_email)

        user.username = admin_username
        user.name = "Admin"
        user.phone = admin_phone
        user.role = "admin"
        user.is_staff = True
        user.is_superuser = True

        if created or not user.has_usable_password():
            user.set_password(admin_password)

        user.save()

        self.stdout.write(self.style.SUCCESS(
            "✅ Admin user created or updated with role=admin"
        ))
