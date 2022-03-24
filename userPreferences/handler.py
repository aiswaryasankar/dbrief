import logging
import numpy as np
import pandas as pd
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sentence_transformers import SentenceTransformer
from logtail import LogtailHandler
import topicModeling.handler as topicModelingHandler
from topicModeling.training import Top2Vec
from rest_framework.response import Response
import datetime
from idl import *
from .repository import *


handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)


"""
  This service handles creating and getting users from the db as well as getting them to follow and unfollow topics.  It also handles recommending and surfacing topics for the user.
"""


def create_user(createUserRequest):
  """
    Creates a user in the database
  """
  createUserRes = createUser(createUserRequest)
  if createUserRes.error != None:
    return CreateUserResponse(
      userId= None,
      error= createUserRes.error
    )

  return createUserRes


def get_user(getUserRequest):
  """
    Gets a user from the database
  """
  getUserRes = getUser(getUserRequest)
  if getUserRes.error != None:
    return GetUserResponse(
      user= None,
      error= getUserRes.error
    )

  return getUserRes



def follow_topic(followTopicRequest):
  """
    Gets a user to follow a topic
  """
  followTopicRes = followTopic(followTopicRequest)

  return followTopicRes



def unfollow_topic(unfollowTopicRequest):
  """
    Gets a user to unfollow a topic
  """
  unfollowTopicRes = unfollowTopic(unfollowTopicRequest)

  return unfollowTopicRes



def get_recommended_topics_for_user(getRecommendedTopicsForUserRequest):
  """
    Gets a list of the recommended topics for a given user
  """
  # Queries the UserTopic database for the topics that the user currently follows
  getTopicsYouFollowRes = getTopicsYouFollow(
    GetTopicsForUserRequest(
      user_id=getRecommendedTopicsForUserRequest.user_id,
    )
  )
  if getTopicsYouFollowRes.error != None:
    return GetRecommendedTopicsForUserResponse(
      topics= None,
      error = str(getTopicsYouFollowRes.error),
    )
  currentTopics = getTopicsYouFollowRes.topics
  logger.info("currentTopics")
  logger.info(currentTopics)

  # If the user isn't following any topics get the top topics currently
  if len(currentTopics) < 5:
    fetchTopicInfoBatchResponse = topicModelingHandler.fetch_random_topic_info_batch()
    if fetchTopicInfoBatchResponse.error != None :
      return GetRecommendedTopicsForUserResponse(
        topics= None,
        error = str(fetchTopicInfoBatchResponse.error),
      )
    else:
      return GetRecommendedTopicsForUserResponse(
        topics= fetchTopicInfoBatchResponse.topics,
        error = fetchTopicInfoBatchResponse.error,
      )

  logger.info("Current topics ")
  logger.info(currentTopics)
  # Hydrates the topics corresponding to those topicIds from the topic database
  fetchTopicInfoBatchResponse = topicModelingHandler.fetch_topic_infos_batch(
    FetchTopicInfoBatchRequest(
      topicIds=currentTopics,
    )
  )
  if fetchTopicInfoBatchResponse.error != None :
    return GetRecommendedTopicsForUserResponse(
      topics= None,
      error = str(fetchTopicInfoBatchResponse.error),
    )

  logger.info("topicInfos")
  logger.info(fetchTopicInfoBatchResponse.topics)

  topics = []
  for topic in fetchTopicInfoBatchResponse.topics[:7]:
    # Queries for topics similar to the existing topics
    searchTopicsResponse = topicModelingHandler.search_topics(
      SearchTopicsRequest(
        keywords=[topic.TopicName],
        num_topics=5,
      )
    )
    if searchTopicsResponse.error != None:
      logger.info("Failed to search topics")
      continue

    topics.extend(searchTopicsResponse.topics_words)

  logger.info("searched topics")
  logger.info(topics)
  topics = list(set(topics))

  # Query for topicInfo given the topic words
  # Hydrates the topics corresponding to those topicIds from the topic database
  fetchTopicInfoBatchResponse = topicModelingHandler.fetch_topic_infos_batch(
    FetchTopicInfoBatchRequest(
      topicNames=topics,
    )
  )
  if fetchTopicInfoBatchResponse.error != None :
    return GetRecommendedTopicsForUserResponse(
      topics= fetchTopicInfoBatchResponse.topics,
      error = fetchTopicInfoBatchResponse.error,
    )

  logger.info("recommended topic infos")
  logger.info(fetchTopicInfoBatchResponse.topics)

  # Returns a list of the top topics returned up to num_topics, default 5
  return GetRecommendedTopicsForUserResponse(
    topics= fetchTopicInfoBatchResponse.topics,
    error = None,
  )


def get_topics_you_follow(getTopicsYouFollowRequest):
  """
    Gets a list of the topics a user follows
  """
  # Fetches the topics in the UserTopic database that correspond to the given user
  getTopicsYouFollowRes = getTopicsYouFollow(
    getTopicsYouFollowRequest
  )
  if getTopicsYouFollowRes.error != None:
    return GetTopicsForUserResponse(
      topics= None,
      error= str(getTopicsYouFollowRes.error),
    )
  currentTopics = getTopicsYouFollowRes.topics
  logger.info("currentTopics")
  logger.info(currentTopics)

  # Hydrates the topics corresponding to those topicIds from the topic database
  fetchTopicInfoBatchResponse = topicModelingHandler.fetch_topic_infos_batch(
    FetchTopicInfoBatchRequest(
      topicIds=currentTopics,
    )
  )
  if fetchTopicInfoBatchResponse.error != None :
    print("FetchTopicInfosBatch error")
    return GetTopicsForUserResponse(
      topics=[],
      error=fetchTopicInfoBatchResponse.error,
    )

  logger.info("topicInfos")
  logger.info(fetchTopicInfoBatchResponse.topics)

  # Returns the list of topicInfo entities
  return GetTopicsForUserResponse(
    topics= fetchTopicInfoBatchResponse.topics,
    error=None,
  )


