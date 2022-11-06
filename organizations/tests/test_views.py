from django import test
from django.test import Client
from django.test import TestCase

"""
  This file will handle checking that all the endpoints are properly called and have a 200 response code.  More advanced functionality can be tested in the future.
"""


class OragnizationViewTest(TestCase):

  def test_create_organization(self):
    response = self.client.post('/createOrganization/', data={
        "name": "name",
        "description": "This organization saves the country from wildfires.",
        "link": "url",
        "image": "image",
        "backgroundImage": "backgroundImage",
        "location": "location",
    }, content_type="application/json")
    self.assertEqual(response.status_code, 200)


  def test_generate_recommended_orgs_for_news_info_card_uuid(self):
    response = self.client.post('/generateRecommendedOrgsForNewsInfoCard/', data= {
      "newsInfoCardUUID": "newsInfoCardUUID",
    })
    self.assertEqual(response.status_code, 200)


  def test_generate_recommended_orgs_for_news_info_card_article(self):
    response = self.client.post('/generateRecommendedOrgsForNewsInfoCard/', data= {
      "newsInfoCard": {
        "uuid": "uuid",
        "title": "title",
        "summary": "summary",
        "isPolitical": True,
        "image": "imageURL",
        "leftOpinionCard": {
          "uuid": "opinionUUID",
          "summary": "opinionSummary",
          "articleURLList": ["url1"],
        },
        "rightOpinionCard": {
          "uuid": "opinionUUID",
          "summary": "opinionSummary",
          "articleURLList": ["url1"],
        },
        "articleList": ["url1", "url2"]
      },
    })
    self.assertEqual(response.status_code, 200)


  def test_get_recommended_orgs_for_news_info_card_uuid(self):
    response = self.client.post('/getRecommendedOrgsForNewsInfoCard/', data= {
      "newsInfoCardUUID": "newsInfoCardUUID",
    })
    self.assertEqual(response.status_code, 200)


  def test_get_recommended_orgs_for_news_info_card_article(self):
    response = self.client.post('/getRecommendedOrgsForNewsInfoCard/', data= {
      "newsInfoCard": {
        "uuid": "uuid",
        "title": "title",
        "summary": "summary",
        "isPolitical": True,
        "image": "imageURL",
        "leftOpinionCard": {
          "uuid": "opinionUUID",
          "summary": "opinionSummary",
          "articleURLList": ["url1"],
        },
        "rightOpinionCard": {
          "uuid": "opinionUUID",
          "summary": "opinionSummary",
          "articleURLList": ["url1"],
        },
        "articleList": ["url1", "url2"]
      },
    })
    self.assertEqual(response.status_code, 200)

