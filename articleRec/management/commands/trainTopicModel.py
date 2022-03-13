from django.core.management import BaseCommand
import logging
from logtail import LogtailHandler
from topicModeling.handler import *
import threading

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = []
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class Command(BaseCommand):

  def handle(self, *args, **options):

    logger.info("Started training topic model")
    x = threading.Thread(target=retrain_topic_model, args=())
    x.start()
