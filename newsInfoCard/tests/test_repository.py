from django import test
from django.test import Client
from django.test import TestCase
from idl import *
from articleRec.repository import *
from datetime import datetime

from newsInfoCard.repository import *

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


def test_create_opinion_card_repo(self):
  """
    Tests saving and updating an opinion card
  """
  article1 = Article()
  article2 = Article()
  req = CreateOpinionCardRequest(
    summary="summary",
    articleList= [article1, article2]
  )

  res1 = createOpinionCardRepo(req)
  self.assertIsNone(res1.error)
  self.assertIsNotNone(res1.opinionCard)
  self.assertIsNotNone(res1.opinionCard.uuid)
  self.assertEqual(res1.opinionCard.summary, "summary")


def test_fetch_opinion_card_repo(self):
  """
    Tests saving and updating an opinion card
  """

  article1 = Article()
  article2 = Article()
  req = CreateOpinionCardRequest(
    summary="summary",
    articleList= [article1, article2]
  )

  createOpinionCardRes = createOpinionCardRepo(req)

  # Fetch the corresponding opinion card
  fetchOpinionCardRes = fetchOpinionCardRepo(
    FetchOpinionCardRequest(
      opinionCardUUID=createOpinionCardRes.opinionCard.uuid
    )
  )
  self.assertIsNone(fetchOpinionCardRes.error)
  self.assertIsNotNone(fetchOpinionCardRes.opinionCard)
  self.assertIsNotNone(fetchOpinionCardRes.opinionCard.uuid)
  self.assertEqual(fetchOpinionCardRes.opinionCard.summary, "summary")


def test_fetch_news_info_card_repo(self):
  """
    Tests fetching a news info card
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

  # Fetch the corresponding news info card
  fetchNewsInfoCardRes = fetchNewsInfoCardRepo(
    FetchNewsInfoCardRequest(
      newsInfoCardUUID=res1.newsInfoCard.uuid
    )
  )
  self.assertIsNone(fetchNewsInfoCardRes.error)
  self.assertIsNotNone(fetchNewsInfoCardRes.newsInfoCard.uuid)



def test_fetch_news_info_card_batch_repo(self):
  """
    Tests fetching news info cards in batch
  """
  req1 = CreateNewsInfoCardRepoRequest(
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
  res1 = createNewsInfoCardRepo(req1)
  self.assertIsNone(res1.error)
  self.assertIsNotNone(res1.newsInfoCard.uuid)

  req2 = CreateNewsInfoCardRepoRequest(
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
  res2 = createNewsInfoCardRepo(req2)
  self.assertIsNone(res2.error)
  self.assertIsNotNone(res2.newsInfoCard.uuid)

  # Fetch the first batch of news info cards
  fetchNewsInfoCardBatch1Res = fetchNewsInfoCardBatchRepo(
    FetchNewsInfoCardBatchRequest(
      offset=0,
      pageSize=1,
    )
  )
  self.assertIsNone(fetchNewsInfoCardBatch1Res.error)
  self.assertIsNotNone(fetchNewsInfoCardBatch1Res.newsInfoCards)
  self.assertEqual(len(fetchNewsInfoCardBatch1Res.newsInfoCards), 1)


  # Fetch the next batch of news info cards
  fetchNewsInfoCardBatch2Res = fetchNewsInfoCardBatchRepo(
    FetchNewsInfoCardBatchRequest(
      offset=1,
      pageSize=1,
    )
  )
  self.assertIsNone(fetchNewsInfoCardBatch2Res.error)
  self.assertIsNotNone(fetchNewsInfoCardBatch2Res.newsInfoCards)
  self.assertEqual(len(fetchNewsInfoCardBatch2Res.newsInfoCards), 1)



def test_set_user_engagement_for_news_info_card_repo(self):
  """
    Tests setting user engagement for each news info card
  """

  req = SetUserEngagementForNewsInfoCardRequest(
    userUUID="userUUID",
    newsInfoCardUUID="newsInfoCardUUID",
    engagementType="right"
  )

  res1 = setUserEngagementForNewsInfoCardRepo(req)
  self.assertIsNone(res1.error)

