from django.core.management import BaseCommand
import logging
from logtail import LogtailHandler

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = []
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class Command(BaseCommand):

  def handle(self, *args, **options):

    print("Started cron job")
    logging.info("Started cron job")
    self.stdout.write("Started the cron job", ending='')
