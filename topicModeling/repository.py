"""
  This file will handle CRUD operations around topics and parent topics in the topic database.
  Topics will be generated by the topic model and stored here in order to quickly retrieve parent topics to serve for
  each of the original topics.
"""

from .models import TopicModel
import logging
from idl import *
from logtail import LogtailHandler
import random
from datetime import datetime, timedelta

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


def deleteTopicsByTimeRange(deleteTopicsByTimeRangeRequest):
  """
    This will delete the topics that were generated prior to the last x days
  """

  deleted_topic_ids = []
  numDays = deleteTopicsByTimeRangeRequest.num_days
  time_threshold = datetime.now() - timedelta(days = numDays)

  if numDays < 5:
    return 0, "Invalid date range"

  for topic in TopicModel.objects.filter(createdAt__lt=time_threshold):
    deleted_topic_ids.append(topic.topicId)
    topic.delete()

  logger.info(deleted_topic_ids)
  logger.info("Number of topics to delete %s", len(deleted_topic_ids))
  return DeleteTopicsByDateRangeResponse(
    num_topics_deleted=len(deleted_topic_ids),
    error=None,
  )


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
          createdAt = str(datetime.now()),
      )

      topicEntry.save()
      logger.info("Saved topic to the database %s", topicEntity.TopicName)
      ids.append(topicEntry.topicId)

    except Exception as e:
      logger.warn("Failed to save topic to the database %s", topicEntity.TopicName)
      logger.warn(e)
      continue

  return CreateTopicsResponse(ids=ids, error=None)


def fetchRandomTopicInfoBatch():
  """
    Fetches random top topics and returns to the user.
  """
  topicInfos = []
  topicInfoEntities = TopicModel.objects.all()

  for topicInfoEntity in topicInfoEntities:
    topicInfo = TopicInfo(
      TopicID=topicInfoEntity.topicId,
      TopicName=topicInfoEntity.topic,
      ParentTopicName=topicInfoEntity.parentTopic,
    )

    topicInfos.append(topicInfo)

  random.shuffle(topicInfos)
  return FetchTopicInfoBatchResponse(
    topics=topicInfos[:7],
    error=None,
  )


def fetchTopicInfoBatch(fetchTopicInfoBatchRequest):
  """
    Will fetch the topicInfo given the topic names.
  """

  topicInfos = []
  searchParams, isIds = [], False

  if fetchTopicInfoBatchRequest.topicIds != []:
    searchParams = fetchTopicInfoBatchRequest.topicIds
    isIds = True
  else:
    searchParams = fetchTopicInfoBatchRequest.topicNames
    isIds = False

  for val in searchParams:
    try:
      if isIds:
        topicInfoEntity = TopicModel.objects.get(topicId=val)
      else:
        topicInfoEntity = TopicModel.objects.filter(topic=val)[0]


      topicInfo = TopicInfo(
          TopicID=topicInfoEntity.topicId,
          TopicName=topicInfoEntity.topic,
          ParentTopicName=topicInfoEntity.parentTopic,
        )

      topicInfos.append(topicInfo)

    except Exception as e:
      print("failed to fetch topic from database")
      logger.warn("Failed to fetch topic from database", extra={
        "searchField": val,
        "error": e,
      })
      logger.info(e)
      continue

  return FetchTopicInfoBatchResponse(
    topics=topicInfos,
    error=None,
  )


def fetchAllTopics():
  """
    Fetches all the topics in the db
  """
  topicList = []
  for topic in TopicModel.objects.all():
      try:
        topicInfo = TopicInfo(
            TopicID=topic.topicId,
            TopicName=topic.topic,
            ParentTopicName=topic.parentTopic,
          )
        topicList.append(topicInfo)
      except Exception as e:
        logger.warn("Failed to fetch fetch topic")
        print(e)

  return FetchTopicInfoBatchResponse(
    topics=topicList,
    error=None,
  )

