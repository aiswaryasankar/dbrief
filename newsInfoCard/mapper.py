from .models import *
import logging
from idl import *
from logtail import LogtailHandler
from datetime import datetime, timedelta
import uuid

"""
  This file will handle mappers for the newsInfoCard service
"""

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)


def OpinionCardModelToEntity(opinionCardModel):
  """
    Will convert an opinion card db model to an internal/ external Opinion Card entity
  """
  opinionCard = OpinionCard(
    uuid = opinionCardModel.uuid,
    summary = opinionCardModel.summary,
    articleURLList = opinionCardModel.articleURLList,
    articleTitleList = opinionCardModel.articleTitleList,
  )

  return opinionCard
