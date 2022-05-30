from django import test
from django.test import Client
from django.test import TestCase

"""
  This file will handle checking that all the endpoints are properly called and have a 200 response code.  More advanced functionality can be tested in the future.
"""


class ArticleRecViewTest(TestCase):
  fixtures=["articleRec.yaml"]

  def test_hello_world(self):
    response = self.client.post('/home/', data={"name": "aiswarya"}, content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_hydrate_article(self):
    response = self.client.post('/hydrateArticle/', data={"url": "https://www.nytimes.com/2022/01/03/world/europe/eu-hungary-threat.html"}, content_type="application/json")
    self.assertEqual(response.status_code, 200)

  # def test_populate_articles_batch(self):
  #   response = self.client.get('/populateArticles/')
  #   self.assertEqual(response.status_code, 200)

  def test_populate_article_by_url(self):
    response = self.client.post('/populateArticle/', data={"url":"https://www.nytimes.com/2022/01/03/world/europe/eu-hungary-threat.html"}, content_type="application/json")
    self.assertEqual(response.status_code, 200)
    print(response.data)

  def test_fetch_articles(self):
    response = self.client.get('/fetchArticles/', content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_fetch_articles_by_num_days(self):
    response = self.client.get('/fetchArticles/', data={"numDays":2}, content_type="application/json")
    self.assertEqual(response.status_code, 200)
    print(response.data)


  def test_delete_articles(self):
    response = self.client.post('/deleteArticles/', data={"numDays":100}, content_type="application/json")
    self.assertEqual(response.status_code, 200)
    print(response.data)


  def test_article_backfill_force_update(self):
    response = self.client.post('/articleBackfill/', data={"force_update": False, "fields": ["topic"]}, content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_article_backfill_fill_empty(self):
    response = self.client.post('/articleBackfill/', data={"force_update": True, "fields": ["topic"]}, content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_article_backfill_parent_topic(self):
    response = self.client.post('/articleBackfill/', data={"force_update": False, "fields": ["parent_topic"]}, content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_article_backfill_passage(self):
    response = self.client.post('/articleBackfill/', data={"force_update": False, "fields": ["top_passage"]}, content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_article_backfill_fact(self):
    response = self.client.post('/articleBackfill/', data={"force_update": False, "fields": ["top_fact"]}, content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_article_backfill_polarity(self):
    response = self.client.post('/articleBackfill/', data={"force_update": False, "fields": ["polarization_score"]}, content_type="application/json")
    self.assertEqual(response.status_code, 200)

