from django import test
from django.test import Client
from django.test import TestCase

"""
  This file will handle checking that all the endpoints are properly called and have a 200 response code.  More advanced functionality can be tested in the future.
"""


class ArticleRecViewTest(TestCase):

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
    response = self.client.get('/fetchArticles/')
    self.assertEqual(response.status_code, 200)


