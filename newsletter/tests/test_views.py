from django.test import TestCase
from django import test
from django.test import Client


"""
  This file will handle checking that all the endpoints are properly called and have a 200 response code.  More advanced functionality can be tested in the future.
"""


class NewsletterViewTest(TestCase):

  def test_create_newsletter(self):

    response = self.client.post('/createNewsletterConfig/',
			data={
				"newsletterConfig": {
					"NewsletterConfigId": 1,
					"UserID": 1,
					"DeliveryTime": "MORNING",
					"RecurrenceType": "DAILY",
					"IsEnabled": True,
					"TopicsFollowed": [1]
				}
			}
		, content_type="application/json")
    self.assertIsNotNone(response.content)
    self.assertEqual(response.status_code, 200)


"""
Create_newsletter_config_for_user

{
	"newsletterConfig": {
		"NewsletterConfigId": 1,
		"UserID": 1,
		"DeliveryTime": "MORNING",
		"RecurrenceType": "DAILY",
		"IsEnabled": true,
		"TopicsFollowed": [1]
	}
}


"""