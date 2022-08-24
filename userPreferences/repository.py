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
    userEntry = UserModel(
      firstName= user.FirstName,
      lastName= user.LastName,
      email= user.Email,
      firebaseAuthId= user.FirebaseAuthID,
    )
    userEntry.save()
    logger.info("Saved user to the database: ", extra={ "user": userEntry })

  except Exception as e:
    logger.info("Failed to save user topic to the database", extra= {
      "user": userEntry.userId,
      "error": e,
    })

    return CreateUserResponse(userId=None, error=str(e))

  return CreateUserResponse(userId=userEntry.userId, error=None)


def getUser(getUserRequest):
  """
    Will get the user from the db
  """

  try:
    if getUserRequest.firebaseAuthId != "":
      user = UserModel.objects.get(firebaseAuthId=getUserRequest.firebaseAuthId)
    elif getUserRequest.userId != 0:
      user = UserModel.objects.get(userId=getUserRequest.userId)
    try:
      user = User(
          FirebaseAuthID=getUserRequest.firebaseAuthId,
          FirstName=user.firstName,
          LastName=user.lastName,
          Email=user.email,
          UserId=user.userId,
        )
    except Exception as e:
      logger.info("Failed to fetch user from database " + str(e))
      print(e)
      return GetUserResponse(
        user=None,
        error=str(e),
      )

  except Exception as e:
    logger.info("Failed to fetch user : " + str(e))
    return GetUserResponse(
      user=None,
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
  forNewsletter = followTopicRequest.forNewsletter

  try:
    topicPair = UserTopicModel.objects.get(topicId=topicId, userId=userId)
  except Exception as e:
    try:
      userTopicEntry = UserTopicModel(
          userId= userId,
          topicId= topicId,
          forNewsletter = forNewsletter,
      )
      userTopicEntry.save()
      logger.info("Saved topic to the database: ", extra={ "topic": userTopicEntry })
      return FollowTopicResponse(userTopicId=userTopicEntry.userTopicId, error=None)

    except Exception as e:
      logger.info("Failed to save user topic to the database", extra= {
        "user": userId,
        "error": e,
      })

      return FollowTopicResponse(userTopicId=None, error=str(e))

  return FollowTopicResponse(userTopicId=topicPair.userTopicId, error=None)


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
  forNewsletter = getTopicsYouFollowRequest.for_newsletter

  try:
    followedTopics = UserTopicModel.objects.filter(userId=userId, forNewsletter=forNewsletter)

  except Exception as e:
    logger.warn("Failed to get topics for user %s", userId)
    return GetTopicsYouFollowResponse(
      topics=None,
      error=str(e)
    )

  for topic in followedTopics:
    topicList.append(topic.topicId)

  return GetTopicsYouFollowResponse(
    topics=topicList,
    error=None
  )


