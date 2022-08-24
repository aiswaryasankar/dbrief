from getpass import getuser
from webbrowser import get
from django import test
from django.test import Client
from django.test import TestCase
from idl import *
from userPreferences.repository import *
from datetime import datetime
from django.db import transaction

"""
  This file will handle testing out all the repository functions and making sure they behave under multiple writes, reads, updates, deletes and invalid data cases.
"""


class UserPreferencesRepoTest(TestCase):

  def test_create_and_get_user(self):
    """
      Tests creating and getting a user
    """
    user1 = User(
      FirebaseAuthID= "testFirebaseAuthId",
      FirstName= "testFirstName",
      LastName= "testLastName",
      Email= "testEmail",
    )
    req = CreateUserRequest(
      user = user1,
    )
    res1 = createUser(req)
    self.assertIsNone(res1.error)
    self.assertEqual(res1.userId, 1)

    # Try creating the same user again - should error
    duplicateUser1 = User(
      FirebaseAuthID= "testFirebaseAuthId",
      FirstName= "testFirstName",
      LastName= "testLastName",
      Email= "testEmail",
    )
    req = CreateUserRequest(
      user = duplicateUser1,
    )

    res2 = createUser(req)
    self.assertIsNotNone(res2.error)
    self.assertIsNone(res2.userId)

    # Try to fetch the user from the database
    try:
      # Duplicates should be prevented.
      with transaction.atomic():
        getUserRes = getUser(
          GetUserRequest(
            userId=res1.userId
          )
        )
        self.fail('Duplicate question allowed.')
    except Exception as e:
        pass


  def test_follow_and_unfollow_topic(self):
    """
      Tests following and unfollowing a topic
    """

    # Follow the topic
    followTopicReq = FollowTopicRequest(
        userId= 123,
        topicId= 1,
        forNewsletter = False,
    )
    res = followTopic(followTopicReq)
    self.assertIsNone(res.error)
    self.assertIsNotNone(res.userTopicId)


    # Get all topics you follow
    getTopicsYouFollowReq = GetTopicsForUserRequest(
      user_id=123,
    )
    res = getTopicsYouFollow(
      getTopicsYouFollowRequest=getTopicsYouFollowReq
    )
    self.assertIsNone(res.error)
    self.assertEqual(res.topics, [1])


    # Unfollow the topic
    unfollowTopicRes = unfollowTopic(
      unfollowTopicRequest=UnfollowTopicRequest(
        userId=123,
        topicId=1,
      )
    )
    self.assertIsNone(unfollowTopicRes.error)


    # Get all topics you follow
    getTopicsYouFollowReq = GetTopicsForUserRequest(
      user_id=123,
    )
    res = getTopicsYouFollow(
      getTopicsYouFollowRequest=getTopicsYouFollowReq
    )
    self.assertIsNone(res.error)
    self.assertEqual(res.topics, [])


  def test_follow_topic_for_newsletter(self):
    """
      Follow a topic for newsletter and fetch all topics for a user that are newsletter.
    """
    # Follow topic for newsletter
    followTopicReq = FollowTopicRequest(
        userId= 123,
        topicId= 1,
        forNewsletter = True,
    )
    res = followTopic(followTopicReq)
    self.assertIsNone(res.error)
    self.assertIsNotNone(res.userTopicId)

    # Follow topic not for newsletter
    followTopicReq = FollowTopicRequest(
        userId= 123,
        topicId= 2,
        forNewsletter = False,
    )
    res = followTopic(followTopicReq)
    self.assertIsNone(res.error)
    self.assertIsNotNone(res.userTopicId)

    # Get all topics you follow
    getTopicsYouFollowReq = GetTopicsForUserRequest(
      user_id=123,
      for_newsletter=True
    )
    res = getTopicsYouFollow(
      getTopicsYouFollowRequest=getTopicsYouFollowReq
    )
    self.assertIsNone(res.error)
    self.assertEqual(res.topics, [1])

    # Get all topics you follow
    getTopicsYouFollowReq = GetTopicsForUserRequest(
      user_id=123,
      for_newsletter=False
    )
    res = getTopicsYouFollow(
      getTopicsYouFollowRequest=getTopicsYouFollowReq
    )
    self.assertIsNone(res.error)
    self.assertEqual(res.topics, [2])



