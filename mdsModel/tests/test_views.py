from django import test
from django.test import Client
from django.test import TestCase

"""
  This file will handle checking that all the endpoints are properly called and have a 200 response code.  More advanced functionality can be tested in the future.
"""


class MDSViewTest(TestCase):

  # Commented out because we don't want to waste OpenAI usage quota on tests!

  # def test_mds_model(self):
  #   response = self.client.post('/mdsV1/', data={"articles":
  #   """Roger Federer is the world's best tennis player.  He has announced he will retire after playing the Laver Cup.
  #   Serena Williams also recently announced her retirement after playing her final US Open.  She put on an impressive performance. She lost in the third round after beating the second seed.
  #   There has been a massive outpour of love for both of these tennis players as they have both given so much to the sport."""}, content_type="application/json")
  #   self.assertEqual(response.status_code, 200)


  def test_mds_v1_model(self):
    response = self.client.post('/mdsV2/', data={"articles":
    """Roger Federer is the world's best tennis player.  He has announced he will retire after playing the Laver Cup.
    Serena Williams also recently announced her retirement after playing her final US Open.  She put on an impressive performance. She lost in the third round after beating the second seed.
    There has been a massive outpour of love for both of these tennis players as they have both given so much to the sport."""}, content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_mds_v2_model(self):
    response = self.client.post('/mdsV3/', data={"articles":
    """Roger Federer is the world's best tennis player.  He has announced he will retire after playing the Laver Cup.
    Serena Williams also recently announced her retirement after playing her final US Open.  She put on an impressive performance. She lost in the third round after beating the second seed.
    There has been a massive outpour of love for both of these tennis players as they have both given so much to the sport."""}, content_type="application/json")
    self.assertEqual(response.status_code, 200)