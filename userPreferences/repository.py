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
        'firstName': user.FirstName,
        'lastName': user.LastName,
        'email': user.Email,
        'firebaseAuthId': user.FirebaseAuthID,
      },
    )
    if created:
      logger.info('saved user', extra={
          "item": {
            'firstName': user.FirstName,
            'lastName': user.LastName,
            'email': user.Email,
            'firebaseAuthId': user.FirebaseAuthID,
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

    return CreateUserResponse(userId=None, error=str(e))

  return CreateUserResponse(userId=userEntry.userId, error=None)


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
        error=str(e),
      )

  return GetUserResponse(
    user=user,
    error=None,
  )


def followTopic(followTopicRequest):
  """
    Will create an entry in the UserTopic table associating the user and the topic
  """

  userId = followTopicRequest.userId
  topicId = followTopicRequest.topicId

  try:
    userTopicEntry = UserTopicModel(
        userId= userId,
        topicId= topicId,
    )
    userTopicEntry.save()
    logger.info("Saved topic to the database: ", extra={ "topic": userTopicEntry })

  except Exception as e:
    logger.info("Failed to save user topic to the database", extra= {
      "user": userId,
      "error": e,
    })

    return FollowTopicResponse(userTopicId=None, error=str(e))

  return FollowTopicResponse(userTopicId=userTopicEntry.userTopicId, error=None)


def unfollowTopic(unfollowTopicRequest):
  """
    Will remove an entry in the UserTopic table associating the user and the topic
  """

  userId = unfollowTopicRequest.userId
  topicId = unfollowTopicRequest.topicId

  try:
    numDeleted, obj = UserTopicModel.objects.filter(userId=userId, topicId=topicId).delete()
    if numDeleted > 0:
      logger.info('deleted user topic pair', extra={
          "item": {
            'userId': userId,
            'topicId': topicId,
          }
      })
      logger.info("Deleted userTopic from the database: ", extra={ "userTopic": obj })
    else:
      logger.info("UserTopic not in the database")

  except Exception as e:
    logger.warn("Failed to delete user topic from the database", extra= {
      "user": userId,
      "topicId": topicId,
      "error": e,
    })

    return UnfollowTopicResponse(error=str(e))

  return UnfollowTopicResponse(error=None)


def getTopicsYouFollow(getTopicsYouFollowRequest):
  """
    Gets the topics a user follows in the UserTopic table
  """

  topicList = []
  userId = getTopicsYouFollowRequest.user_id
  followedTopics = UserTopicModel.objects.filter(userId=userId)

  for topic in followedTopics:
    topicList.append(topic.topicId)

  return topicList


