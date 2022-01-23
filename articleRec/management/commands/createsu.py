from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import logging
from logtail import LogtailHandler


handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)

class Command(BaseCommand):

    def handle(self, *args, **options):
        logger.info("Creating the admin user")
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@admin.com", "admin")