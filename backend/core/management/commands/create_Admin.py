import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create initial Django superuser"

    def handle(self, *args, **kwargs):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not all([username, email, password]):
            self.stdout.write(
                self.style.WARNING("Superuser environment variables missing.")
            )
            return

        User = get_user_model()

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email},
        )

        if created:
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()

            self.stdout.write(
                self.style.SUCCESS("Superuser created successfully.")
            )
        else:
            self.stdout.write(
                self.style.WARNING("Superuser already exists.")
            )
            
