from django import test
from django.test import Client
from django.test import TestCase
from idl import *
from articleRec.repository import *
from datetime import datetime

from newsInfoCard.repository import createNewsInfoCardRepo

"""
  This file will handle testing out all the repository functions and making sure they behave under multiple writes, reads, updates, deletes and invalid data cases.
"""


class NewsInfoCardRepoTest(TestCase):

  def test_save_and_update_news_info_card(self):
    """
      Tests saving and updating a news info card
    """
    req = CreateNewsInfoCardRepoRequest(
      url= "url",
      image= "image",
      publish_date= "publish_date",
      author= "author",
      is_political= True,
      topic= "topic",
      leftOpinionCardUUID = "leftOpinionCardUUID",
      rightOpinionCardUUID = "rightOpinionCardUUID",
      title = "title",
      source = "source",
      summary = "summary",
      articleTitleList = "",
      articleUrlList = "",
    )
    res1 = createNewsInfoCardRepo(req)
    self.assertIsNone(res1.error)
    self.assertIsNotNone(res1.newsInfoCard.uuid)

