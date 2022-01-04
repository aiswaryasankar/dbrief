from django import test
from django.test import Client
from django.test import TestCase

"""
  This file will handle checking that all the endpoints are properly called and have a 200 response code.  More advanced functionality can be tested in the future.
"""


class TopicModelingViewTest(TestCase):

  fixtures=["articleRec.yaml"]

  def test_retrain_topic_model(self):
    response = self.client.get('/trainTopicModel/')
    self.assertEqual(response.status_code, 200)


  def test_get_document_topic(self):
    response = self.client.post('/getDocumentTopic/', data={"doc_ids":[1], "reduced":False, "num_topics":1}, content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_add_document(self):
    response = self.client.post('/addDocument/', data={"url":"https://www.nytimes.com/2022/01/03/world/europe/eu-hungary-threat.html"}, content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_query_documents_by_url(self):
    response = self.client.post('/queryDocumentsByUrl/', content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_search_documents_by_topic(self):
    response = self.client.post('/searchDocumentsByTopic/', content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_search_topics(self):
    response = self.client.post('/searchTopics/', content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_generate_topic_pairs(self):
    response = self.client.post('/generateTopicPairs/')
    self.assertEqual(response.status_code, 200)


