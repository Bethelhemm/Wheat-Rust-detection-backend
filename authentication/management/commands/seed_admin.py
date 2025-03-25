from django.core.management.base import BaseCommand
from authentication.models import User
from decouple import config

class Command(BaseCommand):
    help = "Seed the initial admin user"

    def handle(self, *args, **kwargs):
        admin_email = config("ADMIN_EMAIL")
        admin_phone = config("ADMIN_PHONE")
        admin_password = config("ADMIN_PASSWORD")

        if not User.objects.filter(email=admin_email).exists():
            User.objects.create_superuser(
                name="Admin",
                email=admin_email,
                phone=admin_phone,
                password=admin_password,
                role="admin"
            )
            self.stdout.write(self.style.SUCCESS(f"Admin user created with email {admin_email}"))
        else:
            self.stdout.write(self.style.WARNING("Admin user already exists!"))
