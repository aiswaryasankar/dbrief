import logging
import numpy as np
import pandas as pd
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sentence_transformers import SentenceTransformer
from logtail import LogtailHandler
from topicModeling.training import Top2Vec
from rest_framework.response import Response
import datetime
from idl import *
from repository import *


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
      user= None,
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




def unfollow_topic(unfollowTopicRequest):
  """
    Gets a user to unfollow a topic
  """




def get_recommended_topics_for_user(getRecommendedTopicsForUserRequest):
  """
    Gets a list of the recommended topics for a given user
  """




def get_topics_you_follow(getTopicsYouFollowRequest):
  """
    Gets a list of the topics a user follows
  """



