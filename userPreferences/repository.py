from .models import UserModel, UserTopicModel
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


def createUser(createUserRequest):
  """
    Will save the user to the database.  If the user already exists it will update the existing user instead.
  """

  user = createUserRequest.user

  try:
    userEntry, created = UserModel.objects.update_or_create(
      defaults={
        'firstName': user.firstName,
        'lastName': user.lastName,
        'email': user.email,
        'firebaseAuthId': user.firebaseAuthId,
      },
    )
    if created:
      logger.info('saved user', extra={
          "item": {
            'firstName': user.firstName,
            'lastName': user.lastName,
            'email': user.email,
            'firebaseAuthId': user.firebaseAuthId,
            "created": created,
          }
      })
      logger.info("Saved user to the database: ", extra={ "user": userEntry })
    else:
      logger.info("Updated already existing user")

  except Exception as e:
    logger.warn("Failed to save user to the database", extra= {
      "user": user,
      "error": e,
    })

    return CreateUserResponse(id=None, error=e, created=created)

  return CreateUserResponse(id=userEntry.userId, error=None, created=created)


def getUser(getUserRequest):
  """
    Will get the user from the db
  """

  for user in UserModel.objects.get(userId=id):
    try:
      user = User(
          FirstName=user.firstName,
          LastName=user.lastName,
          EmailAddress=user.email,
          UserID=user.id,
        )
    except Exception as e:
      logger.warn("Failed to fetch user from database", extra={
        "user": user,
        "error": e,
      })
      print(e)

  return GetUserResponse(
    user=user,
    error=None,
  )


def followTopic(followTopicRequest):
  """
    Will create an entry in the UserTopic table associating the user and the topic
  """

  userId = followTopicRequest.userId
  topic = followTopicRequest.topic

  try:
    userTopicEntry, created = UserTopicModel.objects.update_or_create(
      defaults={
        'userId': userId,
        'topic': topic,
      },
    )
    if created:
      logger.info('saved user topic pair', extra={
          "item": {
            'userId': userId,
            'topic': topic,
            "created": created,
          }
      })
      logger.info("Saved userTopic to the database: ", extra={ "user": userTopicEntry })
    else:
      logger.info("Updated already existing user topic")

  except Exception as e:
    logger.warn("Failed to save user topic to the database", extra= {
      "user": userId,
      "error": e,
    })

    return FollowTopicResponse(id=None, error=e, created=created)

  return FollowTopicResponse(id=userTopicEntry.userTopicId, error=None, created=created)


def unfollowTopic(unfollowTopicRequest):
  """
    Will remove an entry in the UserTopic table associating the user and the topic
  """

  userId = unfollowTopicRequest.userId
  topic = unfollowTopicRequest.topic

  try:
    numDeleted, obj = UserTopicModel.objects.filter(userId=userId, topic=topic).delete()
    if numDeleted > 0:
      logger.info('deleted user topic pair', extra={
          "item": {
            'userId': userId,
            'topic': topic,
          }
      })
      logger.info("Deleted userTopic from the database: ", extra={ "userTopic": obj })
    else:
      logger.info("UserTopic not in the database")

  except Exception as e:
    logger.warn("Failed to delete user topic from the database", extra= {
      "user": userId,
      "topic": topic,
      "error": e,
    })

    return UnfollowTopicResponse(error=e)

  return UnfollowTopicResponse(error=None)


def getTopicsYouFollow(getTopicsYouFollowRequest):
  """
    Gets the topics a user follows in the UserTopic table
  """

  userId = getTopicsYouFollowRequest.user_id
  followedTopics = UserTopicModel.objects.filter(userId=userId)
  topics = []

  for topicEntity in followedTopics:
    topics.append(topicEntity.topic)

  return GetTopicsForUserResponse(
    List
  )


