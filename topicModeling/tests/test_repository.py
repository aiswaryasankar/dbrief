from django import test
from django.test import Client
from django.test import TestCase
from idl import *
from topicModeling.repository import *
from datetime import datetime
from .models import TopicModel

"""
  This file will handle testing out all the repository functions and making sure they behave under multiple writes, reads, updates, deletes and invalid data cases.
"""


class TopicModelRepoTest(TestCase):


  def test_save_topic(self):
    """
      Tests saving a topic in the db
    """

    topicPairs = [["biden", "politics"], ["france", "geopolitics"]]
    createTopicsResponse = createTopics(
      CreateTopicsRequest(
        topics=[TopicInfo(
          TopicID=None,
          TopicName=elem[0],
          ParentTopicName=elem[1],
        ) for elem in topicPairs]
      )
    )

    self.assertIsNone(createTopicsResponse.error)
    self.assertEqual(len(createTopicsResponse.ids), 2)



  def test_delete_topics(self):
    """
      Tests deleting topics within a specific date range.
    """

    # Populate a set of articles into the database
    numDays = 5
    t1 = TopicModel(
        topic= "topic1",
        parentTopic= "parentTopic1",
        createdAt = datetime.now() - timedelta(days = numDays+1),
    )
    t1.save()

    t2 = TopicModel(
        topic= "topic2",
        parentTopic= "parentTopic2",
        createdAt = datetime.now() - timedelta(days = numDays-1),
    )
    t2.save()

    deletedTopicIds, err = deleteTopicsByTimeRange(
      DeleteTopicsByDateRangeRequest(
        num_days=numDays,
      )
    )
    self.assertEqual(deletedTopicIds, [t2.id])
    self.assertIsNone(err)

