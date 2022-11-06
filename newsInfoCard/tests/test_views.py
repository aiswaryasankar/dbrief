from django import test
from django.test import Client
from django.test import TestCase

"""
  This file will handle checking that all the endpoints are properly called and have a 200 response code.  More advanced functionality can be tested in the future.
"""


class NewsInfoCardViewTest(TestCase):

  def test_create_news_info_card_article(self):
    response = self.client.post('/createNewsInfoCard/', data={
      "article": {
        "title": "title",
        "text": "CHINESE LEADERS wanted the mood to be “business as usual”. But the summit between China and the European Union on April 1st will be anything but normal. That is because Russia’s invasion of Ukraine, and China’s cold-blooded response to it, have exposed the limitations of Europe’s old trade-first China policies.",
        "url": "url",
        "author": "author",
        "publish_date": "publish_date",
        "topic": "topic",
        "parent_topic": "parentTopic",
        "top_passage": "topPassage",
        "top_fact": "topFact",
        "polarization_score": 1,
        "image": "image"
    }
    }, content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_create_news_info_card_article_url(self):
    response = self.client.post('/createNewsInfoCard/', data={
      "articleUrl": "https://www.nytimes.com/2022/09/16/us/politics/trump-special-master-justice-dept.html"
    }, content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_create_news_info_card_batch(self):
    response = self.client.post('/createNewsInfoCardBatch/', data={
      "articleList": [
        {
          "title": "title",
          "text": "CHINESE LEADERS wanted the mood to be “business as usual”. But the summit between China and the European Union on April 1st will be anything but normal. That is because Russia’s invasion of Ukraine, and China’s cold-blooded response to it, have exposed the limitations of Europe’s old trade-first China policies.",
          "url": "url",
          "author": "author",
          "publish_date": "publish_date",
          "topic": "topic",
          "parent_topic": "parentTopic",
          "top_passage": "topPassage",
          "top_fact": "topFact",
          "polarization_score": 1,
          "image": "image"
        },
        {
          "title": "title",
          "text": "CHINESE LEADERS wanted the mood to be “business as usual”. But the summit between China and the European Union on April 1st will be anything but normal. That is because Russia’s invasion of Ukraine, and China’s cold-blooded response to it, have exposed the limitations of Europe’s old trade-first China policies.",
          "url": "url",
          "author": "author",
          "publish_date": "publish_date",
          "topic": "topic",
          "parent_topic": "parentTopic",
          "top_passage": "topPassage",
          "top_fact": "topFact",
          "polarization_score": 1,
          "image": "image"
        }
      ]
    }, content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_fetch_news_info_card_batch(self):
    response = self.client.post('/fetchNewsInfoCardFeed/', data={"offset": 10, "pageSize": 10})
    self.assertEqual(response.status_code, 200)


  def test_create_news_info_card_backfill(self):
    response = self.client.post('/createNewsInfoCardBackfill/', data={"numDays": 10})
    self.assertEqual(response.status_code, 200)


  def test_set_user_engagement_for_news_info_card(self):
    response = self.client.post('/setUserEngagementForNewsInfoCard', data={"userUUID": "userUUID", "newsInfoCardUUID": "newsInfoCardUUID", "engagemenType": "right"})
    self.assertEqual(response.status_code, 200)

