from django import test
from django.test import Client
from django.test import TestCase
from idl import *
from topicFeed.repository import *
from datetime import datetime
from .models import TopicPageModel

"""
  This file will handle testing out all the repository functions and making sure they behave under multiple writes, reads, updates, deletes and invalid data cases.
"""


class TopicFeedRepoTest(TestCase):


  def test_save_topic_page(self):
    """
      Tests saving a topic page in the db
    """

    saveTopicPageResponse = saveTopicPage(
      SaveTopicPageRequest(
        topic = "topic",
        topicId =  1,
        summary = "summary",
        title = "title",
        imageURL = "imageURL",
        urls = "url1, url2, url3, url4",
        topArticleId = 5,
        isTimeline = True,
      )
    )

    self.assertIsNone(saveTopicPageResponse.error)
    self.assertEqual(len(saveTopicPageResponse.topicPageId), 1)

