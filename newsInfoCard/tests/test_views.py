from django import test
from django.test import Client
from django.test import TestCase

"""
  This file will handle checking that all the endpoints are properly called and have a 200 response code.  More advanced functionality can be tested in the future.
"""


class NewsInfoCardViewTest(TestCase):

  def test_create_news_info_card_article(self):
    response = self.client.post('/createNewsInfoCard/', data={"article": "hi"}, content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_create_news_info_card_article_url(self):
    response = self.client.post('/createNewsInfoCard/', data={"article": "hi"}, content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_create_news_info_card_batch(self):
    response = self.client.post('/createNewsInfoCardBatch/', data={"article": "hi"}, content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_fetch_news_info_card_batch(self):
    response = self.client.get('/fetchNewsInfoCardFeed/', data={"offset": 10, "limit": 10})
    self.assertEqual(response.status_code, 200)
