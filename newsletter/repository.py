from .models import NewsletterConfigModel
import logging
from idl import *
from logtail import LogtailHandler

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


def createNewsletterConfig(createNewsletterConfigRequest):
  """
    Will create an entry in the UserTopic table associating the user and the topic
  """
  print(createNewsletterConfigRequest)
  newsletterConfig = createNewsletterConfigRequest.newsletterConfig
  print(newsletterConfig)

  try:
    newsletterConfigEntry = NewsletterConfigModel(
      userId = newsletterConfig.UserID,
      deliveryTime = newsletterConfig.DeliveryTime,
      recurrenceType = newsletterConfig.RecurrenceType,
      isEnabled = newsletterConfig.IsEnabled,
    )
    newsletterConfigEntry.save()
    print("Saved newsletter config")
    logger.info("Saved newsletterConfig to the database: ", extra={
      "userId": newsletterConfig.UserID,
    })

  except Exception as e:
    logger.info("Failed to save newsletterConfig to the database", extra= {
      "userId": newsletterConfig.UserID,
    })
    print("failed to create newsletter config")
    return CreateNewsletterConfigForUserResponse(newsletterId=None, error=str(e))

  return CreateNewsletterConfigForUserResponse(
    newsletterId=newsletterConfigEntry.newsletterConfigId,
    error=None
  )


def updateNewsletterConfig(updateNewsletterConfigRequest):
  """
    This will updated the given newsletterConfigId with the updated fields using create_or_update.
  """

  newsletterConfig = updateNewsletterConfigRequest.newsletterConfig
  try:
    newsletterConfigEntry, created = NewsletterConfigModel.objects.update_or_create(
      userId=newsletterConfig.UserID,
      defaults={
        'deliveryTime': newsletterConfig.DeliveryTime,
        'recurrenceType' : newsletterConfig.RecurrenceType,
        'isEnabled': newsletterConfig.IsEnabled,
      },
    )
    if created:
      logger.info('Created newsletter config')
    else:
      logger.info("Updated already existing user")

  except Exception as e:
    logger.warn("Failed to update newsletter config", extra= {
      "config": newsletterConfig,
      "error": e,
    })

    return UpdateNewsletterConfigForUserResponse(
      newsletterId=None,
      error=str(e),
    )

  return UpdateNewsletterConfigForUserResponse(
    newsletterId=newsletterConfigEntry.newsletterConfigId,
    error=None,
  )


def getNewsletterConfig(getNewsletterConfigRequest):
  """
    This will fetch the newsletter config stored by the requested user.
  """
  try:
    newsletterConfig = NewsletterConfigModel.objects.get(userId = getNewsletterConfigRequest.userId)

    # Hydrate the topic from the list of topics included in newsletterConfig
    newsletterConfig = NewsletterConfigV1(
      NewsletterConfigId=newsletterConfig.NewsletterConfigId,
      UserId=newsletterConfig.UserID,
      DeliveryTime=newsletterConfig.DeliveryTime,
      RecurrenceType=newsletterConfig.RecurrenceType,
      IsEnabled=newsletterConfig.IsEnabled,
      TopicsFollowed=newsletterConfig.TopicsFollowed,
    )
    logger.info(newsletterConfig)

  except Exception as e:
    logger.warn("Failed to fetch newsletter config for user: " + str(getNewsletterConfigRequest.userId))

  return GetNewsletterConfigForUserResponse(
    newsletterConfig=newsletterConfig,
    error=None,
  )


def queryNewsletterConfig(queryNewsletterConfigRequest):
  """
    This will query the newsletter config database with the requested fields.
  """
  try:
    configs = NewsletterConfigModel.objects.filter(dayOfWeek=queryNewsletterConfigRequest.DayOfWeek)
    configs = configs | NewsletterConfigModel.objects.filter(deliveryTime=queryNewsletterConfigRequest.DeliveryTime)

    return QueryNewsletterConfigResponse(
      newsletterConfigs=configs,
      error=None,
    )

  except Exception as e:
    logger.warn("Failed to query newsletter configs on days: " + str(queryNewsletterConfigRequest.DayOfWeek))

    return QueryNewsletterConfigResponse(
      newsletterConfigs=None,
      error=str(e),
    )



