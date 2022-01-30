from django import test
from django.test import Client
from django.test import TestCase

"""
  This file will handle checking that all the endpoints are properly called and have a 200 response code.  More advanced functionality can be tested in the future.
"""


class TopicFeedViewTest(TestCase):

  fixtures=["articleRec.yaml", "topics.yaml"]

  def test_get_topic_page_url(self):
    response = self.client.post('/getTopicPage/', data={"url": "https://www.nytimes.com/2022/01/03/world/europe/eu-hungary-threat.html"}, content_type="application/json")
    self.assertIsNotNone(response.content)
    self.assertEqual(response.status_code, 200)


  def test_get_topic_page_text(self):
    response = self.client.post('/getTopicPage/', data={"text": "Ms. Coulter’s anti-Trump bile is not entirely new and carries the bitter fury of a disillusioned believer. While an early and enthusiastic MAGA convert — during the 2016 campaign Ms. Coulter cheekily proclaimed herself ready to die for her candidate and penned a cringey hagiography titled — she began souring on his presidency pretty quickly over his failure to make good on his more draconian immigration promises. (Ann really wanted that border wall.)"}, content_type="application/json")
    self.assertIsNotNone(response.content)
    self.assertEqual(response.status_code, 200)


  def test_get_topic_page_topicName(self):
    response = self.client.post('/getTopicPage/', data={"topicName": "partisanship"}, content_type="application/json")
    self.assertIsNotNone(response.content)
    self.assertEqual(response.status_code, 200)


  def test_get_topic_page_articleId(self):
    response = self.client.post('/getTopicPage/', data={"articleId": 1}, content_type="application/json")
    self.assertIsNotNone(response.content)
    self.assertEqual(response.status_code, 200)


  def test_get_topic_page_articleId_failure(self):
    response = self.client.post('/getTopicPage/', data={"articleId": 1000000}, content_type="application/json")
    self.assertIsNotNone(response.content)
    self.assertEqual(response.status_code, 200)


  def test_whats_happening(self):
    response = self.client.post('/whatsHappening/', data={"user_id": "1"}, content_type="application/json")
    self.assertEqual(response.status_code, 200)
    self.assertIsNotNone(response.content)



