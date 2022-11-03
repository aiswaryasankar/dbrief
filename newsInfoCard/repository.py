from .models import *
import logging
from idl import *
from logtail import LogtailHandler
from datetime import datetime, timedelta
import uuid
from .mapper import *

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



def fetchOpinionCardRepo(fetchOpinionCardRequest):
  """
    Will fetch the appropriate opinion card
  """
  opinionCardUUID = fetchOpinionCardRequest.opinionCardUUID
  opinionCardEntity = None

  try:
      opinionCardRes = OpinionCardModel.objects.get(uuid=opinionCardUUID)
      logger.info("OPINION CARD RES")
      logger.info(opinionCardRes)
      opinionCardEntity = OpinionCardModelToEntity(opinionCardRes)

  except Exception as e:
    logger.warn("Failed to fetch opinion card with uuid: " + str(opinionCardUUID))
    return FetchOpinionCardResponse(
      opinionCard=None,
      error=e,
    )

  return FetchOpinionCardResponse(
    opinionCard=opinionCardEntity,
    error=None,
  )


def fetchNewsInfoCardRepo(fetchNewsInfoCardRequest):
  """
    Will fetch the appropriate newsInfoCard
  """
  newsInfoCardUUID = fetchNewsInfoCardRequest.newsInfoCardUUID
  newsInfoCardEntity = None

  try:
    infoCard = NewsInfoCardModel.objects.get(uuid=newsInfoCardUUID)
    # Hydrate the right and left opinion cards
    rightOpinionCard = fetchOpinionCardRepo(
      FetchOpinionCardRequest(
        opinionCardUUID=infoCard.rightOpinionCardUUID
      )
    )

    leftOpinionCard = fetchOpinionCardRepo(
      FetchOpinionCardRequest(
        opinionCardUUID=infoCard.leftOpinionCardUUID
      )
    )

    newsInfoCardEntity = NewsInfoCard(
      uuid= infoCard.uuid,
      title= infoCard.title,
      summary= infoCard.summary,
      isPolitical= infoCard.is_political,
      leftOpinionCard= leftOpinionCard,
      rightOpinionCard= rightOpinionCard,
      articleList= [],
    )

  except Exception as e:
    logger.warn("Failed to fetch news info card with uuid: " + str(newsInfoCardUUID))
    return FetchNewsInfoCardResponse(
      newsInfoCard=None,
      error=e,
    )

  logger.info(newsInfoCardEntity)

  return FetchNewsInfoCardResponse(
    newsInfoCard=newsInfoCardEntity,
    error=None,
  )


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


def fetchNewsInfoCardBatchRepo(fetchNewsInfoCardBatchRequest):
  """
    Fetches a news info card and hydrates both opinion cards as well
  """
  offset = fetchNewsInfoCardBatchRequest.offset
  pageSize = fetchNewsInfoCardBatchRequest.pageSize
  newsInfoCards = []

  try:
    newsInfoCardsRes = NewsInfoCardModel.objects.all().order_by('-createdAt')[offset:offset+pageSize]

    for infoCard in newsInfoCardsRes:

      # Hydrate the right and left opinion cards
      rightOpinionCard = fetchOpinionCardRepo(
        FetchOpinionCardRequest(
          opinionCardUUID=infoCard.rightOpinionCardUUID
        )
      )

      leftOpinionCard = fetchOpinionCardRepo(
        FetchOpinionCardRequest(
          opinionCardUUID=infoCard.leftOpinionCardUUID
        )
      )

      newsInfoCard = NewsInfoCard(
        uuid= infoCard.uuid,
        title= infoCard.title,
        summary= infoCard.summary,
        isPolitical= infoCard.is_political,
        leftOpinionCard= leftOpinionCard,
        rightOpinionCard= rightOpinionCard,
        articleList= [],
      )

      newsInfoCards.append(newsInfoCard)

  except Exception as e:
    logger.warn("Failed to fetch news info card batch: " + str(e))

    return FetchNewsInfoCardBatchResponse(
      newsInfoCards=None,
      error=e,
    )

  return FetchNewsInfoCardBatchResponse(
    newsInfoCards=newsInfoCards,
    error=None,
  )


def setUserEngagementForNewsInfoCardRepo(setEngagementForNewsInfoCardRequest):
  """
    Will save user engagement for news info card
  """

  interactionUUID = str(uuid.uuid1())

  try:
    interaction, created = UserNewsInfoCardInteractionModel.objects.update_or_create(
      uuid = interactionUUID,
      defaults={
        'newsInfoCardUUID': setEngagementForNewsInfoCardRequest.newsInfoCardUUID,
        'userUUID': setEngagementForNewsInfoCardRequest.userUUID,
        'interaction': setEngagementForNewsInfoCardRequest.engagementType,
      },
    )
    if created:
      logger.info('Saved user interaction')

  except Exception as e:
    logger.warn("Failed to save user interaction to the database: " + str(e))

    return SetUserEngagementForNewsInfoCardResponse(error=e)

  return SetUserEngagementForNewsInfoCardResponse(error=None)

