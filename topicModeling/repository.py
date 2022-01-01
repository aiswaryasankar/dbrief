"""
  This file will handle CRUD operations around topics and parent topics in the topic database.
  Topics will be generated by the topic model and stored here in order to quickly retrieve parent topics to serve for
  each of the original topics.
"""

from .models import TopicModel
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


def createTopics(createTopicRequest):
  """
    Will create the topic in the database.  If the topic already exists it will update the existing topic instead.
  """

  ids = []
  topicPairs = createTopicRequest.topics

  for topicEntity in topicPairs:
    try:
      topicEntry = TopicModel(
          topic= topicEntity.TopicName,
          parentTopic= topicEntity.ParentTopicName,
      )
      topicEntry.save()
      logger.info("Saved topic to the database: ", extra={ "topic": topicEntry })
      ids.append(topicEntry.topicId)

    except Exception as e:
      logger.warn("Failed to save topic to the database", extra= {
        "topic": topicEntity.TopicName,
        "error": e,
      })
      print(e)

      return CreateTopicsResponse(ids=None, error=e)

  return CreateTopicsResponse(ids=ids, error=None)


def fetchTopicInfoBatch(fetchTopicInfoBatchRequest):
  """
    Will fetch the topicInfo given the topic names.
  """
  topicInfos = []
  topicIds = fetchTopicInfoBatchRequest.topicIds

  for topicId in topicIds:

    try:
      topicInfoEntity = TopicModel.objects.get(topicId=topicId)
      print(topicInfoEntity)
      topicInfo = TopicInfo(
          TopicID=topicInfoEntity.topicId,
          TopicName=topicInfoEntity.topic,
          ParentTopicName=topicInfoEntity.parentTopic,
        )

      topicInfos.append(topicInfo)

    except Exception as e:
      logger.warn("Failed to fetch topic from database", extra={
        "topicId": topicId,
        "error": e,
      })
      print(e)
      return FetchTopicInfoBatchResponse(
        topics=topicInfos,
        error=e,
      )

  return FetchTopicInfoBatchResponse(
    topics=topicInfos,
    error=None,
  )


