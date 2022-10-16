from turtle import right
from .models import *
import logging
from idl import *
from logtail import LogtailHandler
from datetime import datetime, timedelta
import uuid

"""
  This file will include all the basic database CRUD operations including:
    - Save
    - Query
    - Delete
    - Update
"""

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)


def createOpinionCardRepo(createOpinionCardRequest):
  """
    Will save the opinion card to the database.
  """

  summary = createOpinionCardRequest.summary
  articleTitleList = [article.title for article in createOpinionCardRequest.articleList]
  articleUrlList = [article.url for article in createOpinionCardRequest.articleList]
  opinionCardUUID = str(uuid.uuid1())

  try:
    opinionCard, created = OpinionCardModel.objects.update_or_create(
      uuid = opinionCardUUID,
      defaults={
        'summary': summary,
        'articleTitleList': articleTitleList,
        'articleUrlList': articleUrlList,
      },
    )
    if created:
      logger.info('Saved opinion card')

  except Exception as e:
    logger.warn("Failed to save opinion card to the database: " + str(e))

    return CreateOpinionCardResponse(opinionCard=None, error=e)

  return CreateOpinionCardResponse(opinionCard=opinionCard, error=None)



def createNewsInfoCardRepo(createNewsInfoCardRepoRequest):
  """
    Creates a news info card
  """

  newsCardUUID = str(uuid.uuid1())
  url = createNewsInfoCardRepoRequest.url
  title = createNewsInfoCardRepoRequest.title
  summary = createNewsInfoCardRepoRequest.summary
  image = createNewsInfoCardRepoRequest.image
  publish_date = createNewsInfoCardRepoRequest.publish_date
  author = createNewsInfoCardRepoRequest.author
  source = createNewsInfoCardRepoRequest.source
  is_political = createNewsInfoCardRepoRequest.is_political
  topic = createNewsInfoCardRepoRequest.topic
  leftOpinionCardUUID = createNewsInfoCardRepoRequest.left_opinion_card_UUID
  rightOpinionCardUUID = createNewsInfoCardRepoRequest.right_opinion_card_UUID
  articleUrlList = createNewsInfoCardRepoRequest.article_url_list
  articleTitleList = createNewsInfoCardRepoRequest.article_title_list


  try:
    newsInfoCard, created = NewsInfoCardModel.objects.update_or_create(
      uuid = newsCardUUID,
      defaults={
        'url': url,
        'image': image,
        'publish_date': publish_date,
        'author': author,
        'is_political': is_political,
        'topic': topic,
        'leftOpinionCardUUID': leftOpinionCardUUID,
        'rightOpinionCardUUID': rightOpinionCardUUID,
        'title': title,
        'source': source,
        'summary': summary,
        'articleTitleList': articleTitleList,
        'articleUrlList': articleUrlList,
      },
    )
    if created:
      logger.info('Saved news info card')

  except Exception as e:
    logger.warn("Failed to save news info card to the database: " + str(e))

    return CreateNewsInfoCardResponse(newsInfoCard=None, error=e)

  return CreateNewsInfoCardResponse(newsInfoCard=newsInfoCard, error=None)




def fetchNewsInfoCardRepo(fetchNewsInfoCardRequest):
  """
    Fetches a news info card
  """
  pass





