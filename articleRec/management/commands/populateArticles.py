from django.core.management import BaseCommand
import logging
from logtail import LogtailHandler
from articleRec.handler import *

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = []
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class Command(BaseCommand):

  def handle(self, *args, **options):

    logger.info("Started cron job")
    res = populate_article(
      PopulateArticleRequest(
        url= "https://www.nytimes.com/2022/03/12/world/europe/ukraine-mayor-kidnapped-ivan-fyodorov.html"
      )
    )
    logger.info(res.error)

