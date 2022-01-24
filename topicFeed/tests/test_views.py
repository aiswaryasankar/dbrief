from django import test
from django.test import Client
from django.test import TestCase

"""
  This file will handle checking that all the endpoints are properly called and have a 200 response code.  More advanced functionality can be tested in the future.
"""


class TopicFeedViewTest(TestCase):

  def test_get_topic_page(self):
    response = self.client.post('/getTopicPage/', data={"source": "https://www.nytimes.com/2022/01/03/world/europe/eu-hungary-threat.html"}, content_type="application/json")
    self.assertIsNotNone(response.content)
    self.assertEqual(response.status_code, 200)


  def test_whats_happening(self):
    response = self.client.post('/whatsHappening/', data={"user_id": "1"}, content_type="application/json")
    self.assertEqual(response.status_code, 200)
    self.assertIsNotNone(response.content)

