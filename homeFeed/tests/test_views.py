from django import test
from django.test import Client
from django.test import TestCase

"""
  This file will handle checking that all the endpoints are properly called and have a 200 response code.  More advanced functionality can be tested in the future.
"""


class HomePageTest(TestCase):

  def test_hydrate_home_page(self):
    response = self.client.post('/hydrateHomePage/', data={"user_id": 1}, content_type="application/json")
    self.assertEqual(response.status_code, 200)

  def test_hydrate_home_page_v2(self):
    response = self.client.post('/hydrateHomePageV2/', data={"user_id": 1}, content_type="application/json")
    self.assertEqual(response.status_code, 200)

