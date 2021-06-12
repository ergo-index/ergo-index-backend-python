from decouple import config
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from backend.ProjectSettings import ProjectSettings


class Command(BaseCommand):

    def handle(self, *args, **options):
        ProjectSettings.setup_and_validate_settings()
        ADMIN_EMAIL = config('ADMIN_EMAIL', cast=str)
        ADMIN_USERNAME = config('ADMIN_USER', cast=str)
        ADMIN_PASSWORD = config('ADMIN_PASSWORD', cast=str)
        print('Creating account for %s (%s)' % (ADMIN_USERNAME, ADMIN_EMAIL))
        admin = User.objects.create_superuser(email=ADMIN_EMAIL, username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        admin.is_active = True
        admin.is_admin = True
        admin.save()
