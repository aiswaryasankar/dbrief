from django import test
from django.test import Client
from django.test import TestCase

"""
  This file will handle checking that all the endpoints are properly called and have a 200 response code.  More advanced functionality can be tested in the future.
"""


class PolarityModelViewTest(TestCase):

  def test_get_document_polarity(self):

    response = self.client.post('/getDocumentPolarity/', data={"query":"Republicans are stupid and wear MAGA hats all day long."}, content_type="application/json")
    self.assertIsNotNone(response.content)
    self.assertEqual(response.status_code, 200)


  def test_get_document_polarity_batch(self):

    response = self.client.post('/getDocumentPolarityBatch/', data={"queryList": ["Democrats live in San Francisco and throw liberal parties."]}, content_type="application/json")
    self.assertEqual(response.status_code, 200)
    self.assertIsNotNone(response.content)

