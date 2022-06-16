from .models import TopicPageModel
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


def saveTopicPage(saveTopicPageRequest):
  """
    Will save the topic page in the database
  """

  try:
    topicPageEntry = TopicPageModel(
      topic = saveTopicPageRequest.topic,
      topicId =  saveTopicPageRequest.topicId,
      summary = saveTopicPageRequest.summary,
      title = saveTopicPageRequest.title,
      imageURL = saveTopicPageRequest.imageURL,
      urls = saveTopicPageRequest.urls,
      topArticleId = saveTopicPageRequest.topArticleId,
      isTimeline = saveTopicPageRequest.isTimeline,
    )

    topicPageEntry.save()
    print("Saved topic page entry")
    logger.info("Saved topic page entry to the database")

  except Exception as e:
    logger.info("Failed to save topic page to the database: " + str(e))
    print("failed to create topic page entry")
    print(e)
    return SaveTopicPageResponse(
      topicPageId=None,
      error=str(e)
    )

  return SaveTopicPageResponse(
    topicPageId=topicPageEntry.topicPageId,
    error=None
  )





