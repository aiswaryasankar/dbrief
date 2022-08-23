from django import test
from django.test import Client
from django.test import TestCase
from idl import *
from articleRec.repository import *
from datetime import datetime

from newsletter.repository import *

"""
  This file will handle testing out all the repository functions and making sure they behave under multiple writes, reads, updates, deletes and invalid data cases.
"""


class NewsletterRepoTest(TestCase):

  def test_create_and_fetch_newsletter_config(self):
    """
      Tests creating and fetching newsletter configs
    """
    newsletterConfig = NewsletterConfigV1 (
      NewsletterConfigId= 1,
      UserID=1,
      DeliveryTime="MORNING",
      RecurrenceType="DAILY",
      IsEnabled=True,
      TopicsFollowed=[1],
    )

    req = CreateNewsletterConfigForUserRequest(
      newsletterConfig=newsletterConfig,
    )
    res1 = updateNewsletterConfig(req)
    self.assertIsNone(res1.error)
    self.assertEqual(res1.newsletterId, 1)

    # Try to create another newsletter for the same user and just check that it updates the same config instead of creating a new one
    newsletterConfig = NewsletterConfigV1 (
      NewsletterConfigId=2,
      UserID=1,
      DeliveryTime="EVENING",
      RecurrenceType="WEEKLY",
      IsEnabled=True,
      TopicsFollowed=[1],
    )
    req = CreateNewsletterConfigForUserRequest(
      newsletterConfig=newsletterConfig,
    )
    res2 = updateNewsletterConfig(req)
    self.assertIsNone(res2.error)
    self.assertEqual(res2.newsletterId, 1)

    # Fetch the newsletter and check it has been updated appropriately
    fetchedNewsletterConfigRes = getNewsletterConfig(
      GetNewsletterConfigForUserRequest(
        userId=1,
      )
    )
    logger.info(fetchedNewsletterConfigRes)
    self.assertIsNone(fetchedNewsletterConfigRes.error)
    self.assertEqual(fetchedNewsletterConfigRes.newsletterConfig.deliveryTime, "EVENING")


  def test_query_newsletter_config(self):
    """
      Tests querying for newsletter configs that match the given day of week and time of day.
    """

    newsletterConfig = NewsletterConfigV1 (
      NewsletterConfigId= 1,
      UserID=1,
      DeliveryTime="MORNING",
      RecurrenceType="DAILY",
      IsEnabled=True,
      TopicsFollowed=[1],
    )

    req = CreateNewsletterConfigForUserRequest(
      newsletterConfig=newsletterConfig,
    )
    res1 = updateNewsletterConfig(req)

    newsletterConfig = NewsletterConfigV1 (
      NewsletterConfigId= 1,
      UserID=1,
      DeliveryTime="MORNING",
      DayOfWeek="DAILY",
      IsEnabled=True,
      TopicsFollowed=[1],
    )

    req = CreateNewsletterConfigForUserRequest(
      newsletterConfig=newsletterConfig,
    )
    res1 = updateNewsletterConfig(req)


