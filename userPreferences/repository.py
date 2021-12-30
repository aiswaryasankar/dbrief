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


