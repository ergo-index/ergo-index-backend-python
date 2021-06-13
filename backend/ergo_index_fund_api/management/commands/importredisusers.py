from decouple import config
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from backend.ProjectSettings import ProjectSettings
from backend.redis.RedisManager import RedisManager


class Command(BaseCommand):
    """
    Browses entire user base from reddit and ensures the users are also present in Django.
    """

    def handle(self, *args, **options):
        ProjectSettings.setup_and_validate_settings()
        redis = RedisManager()
        # TODO Get all users from redis.
        # TODO Check if each user is registered with Django.
        # TODO If a user is not registered, print a warning.
