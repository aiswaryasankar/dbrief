from django import test
from django.test import Client
from django.test import TestCase

"""
  This file will handle checking that all the endpoints are properly called and have a 200 response code.  More advanced functionality can be tested in the future.
"""


class TopicModelingViewTest(TestCase):

  def test_create_user_view(self):
    response = self.client.post('/createUser/', data={
        "user":{
            "FirebaseAuthID":"1",
            "Username":"aiswarya",
            "FirstName":"Aiswarya",
            "LastName":"Sankar",
            "Email":"aiswarya.s@gmail.com"
        }
    }, content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_get_user_view(self):
    response = self.client.post('/getUser/', data={"user_id": "1"}, content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_follow_topic_view(self):
    response = self.client.post('/followTopic/', data={"userId": 1, "topicId": 1, "forNewsletter": True}, content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_unfollow_topic_view(self):
    response = self.client.post('/unfollowTopic/', data={"userId": 1, "topicId": 1, "forNewsletter": True}, content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_get_recommended_topics_for_user_view(self):
    response = self.client.post('/getRecommendedTopics/', data={"user_id":1, "num_topics":1}, content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_get_topics_you_follow_view(self):
    response = self.client.post('/getTopicsYouFollow/', data={"user_id":1}, content_type="application/json")
    self.assertEqual(response.status_code, 200)


