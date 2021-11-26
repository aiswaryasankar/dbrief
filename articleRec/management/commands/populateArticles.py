from django.core.management import BaseCommand


class Command(BaseCommand):

  def handle(self, *args, **options):

    print("Started the cron job")
    handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
    logger = logging.getLogger(__name__)
    logger.handlers = []
    logger.addHandler(handler)
    logger.info('LOGTAIL TEST')