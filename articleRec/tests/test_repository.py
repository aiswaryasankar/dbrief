from django import test
from django.test import Client
from django.test import TestCase
from idl import *
from articleRec.repository import *
from datetime import datetime

"""
  This file will handle testing out all the repository functions and making sure they behave under multiple writes, reads, updates, deletes and invalid data cases.
"""


class ArticleRecRepoTest(TestCase):

  def test_save_and_update_article(self):
    """
      Tests saving and updating an article.
      All validates using incorrect datatypes.
    """
    a1 = Article(
      url = "testUrl",
      title = "testTitle",
      text = "testText",
      authors = ["testAuthor"],
      date = datetime.now(),
      topic = "testTopic",
      parentTopic = "testParentTopic",
      topPassage = "testPassage",
      topFact = "testFact",
      imageURL = "testURL",
      polarizationScore = 0.0,
    )
    req = SaveArticleRequest(
      article = a1,
    )
    res1 = saveArticle(req)
    self.assertIsNone(res1.error)
    self.assertTrue(res1.created)

    a2 = Article(
      id = res1.id,
      url = "testUrl",
      title = "testTitle_updated",
      text = "testText_updated",
      authors = ["testAuthor"],
      date = datetime.now(),
      topic = "testTopic",
      parentTopic = "testParentTopic",
      topPassage = "testPassage",
      topFact = "testFact",
      imageURL = "testURL",
      polarizationScore = 0.0,
    )
    req = SaveArticleRequest(
      article = a2,
    )

    res2 = saveArticle(req)
    self.assertIsNone(res2.error)
    self.assertEqual(res2.id, res1.id)
    self.assertFalse(res2.created)

    # Fetch the article from the database and check it has been updated appropriately
    fetchedArticleRes = fetchArticlesById(
      FetchArticlesRequest(
        articleIds=[res2.id]
      )
    )
    self.assertIsNone(fetchedArticleRes.error)
    self.assertEqual(fetchedArticleRes.articleList[0].title, "testTitle_updated")


  def test_fetch_articles(self):
    """
      Tests fetch_articles after creating the article.
    """
    a1 = Article(
      url = "testUrl",
      title = "testTitle",
      text = "testText",
      authors = ["testAuthor"],
      date = datetime.now(),
      topic = "testTopic",
      parentTopic = "testParentTopic",
      topPassage = "testPassage",
      topFact = "testFact",
      imageURL = "testURL",
      polarizationScore = 0.0,
    )
    req = SaveArticleRequest(
      article = a1,
    )
    res = saveArticle(req)
    self.assertIsNone(res.error)

    fetchedArticleRes = fetchAllArticles()
    self.assertIsNone(fetchedArticleRes.error)
    self.assertEqual(fetchedArticleRes.articleList[0].title, "testTitle")


  def test_query_articles(self):
    """
      Tests out the functionality of retrieving all rows where a specified field is empty.
    """
    a1 = Article(
      url = "testUrl",
      title = "testTitle",
      text = "testText",
      authors = ["testAuthor"],
      date = datetime.now(),
      topic = "",
      parentTopic = "",
      topPassage = "",
      topFact = "",
      imageURL = "testURL",
      polarizationScore = 0,
    )
    req = SaveArticleRequest(
      article = a1,
    )
    res = saveArticle(req)
    self.assertIsNone(res.error)

    a2 = Article(
      url = "testUrl_2",
      title = "testTitle",
      text = "testText",
      authors = ["testAuthor"],
      date = datetime.now(),
      topic = "testTopic",
      parentTopic = "testParentTopic",
      topPassage = "testPassage",
      topFact = "testFact",
      imageURL = "testURL",
      polarizationScore = 0.5,
    )
    req = SaveArticleRequest(
      article = a2,
    )
    res = saveArticle(req)
    self.assertIsNone(res.error)

    queryArticlesRes = queryArticles(
      queryArticleRequest=QueryArticleRequest(
        field="topic"
      )
    )
    self.assertIsNone(queryArticlesRes.error)
    self.assertEqual(len(queryArticlesRes.articles), 1)

    queryArticlesRes = queryArticles(
      queryArticleRequest=QueryArticleRequest(
        field="parent_topic"
      )
    )
    self.assertIsNone(queryArticlesRes.error)
    self.assertEqual(len(queryArticlesRes.articles), 1)

    queryArticlesRes = queryArticles(
      queryArticleRequest=QueryArticleRequest(
        field="top_passage"
      )
    )
    self.assertIsNone(queryArticlesRes.error)
    self.assertEqual(len(queryArticlesRes.articles), 1)

    queryArticlesRes = queryArticles(
      queryArticleRequest=QueryArticleRequest(
        field="top_fact"
      )
    )
    self.assertIsNone(queryArticlesRes.error)
    self.assertEqual(len(queryArticlesRes.articles), 1)

    queryArticlesRes = queryArticles(
      queryArticleRequest=QueryArticleRequest(
        field="polarization_score"
      )
    )
    self.assertIsNone(queryArticlesRes.error)
    self.assertEqual(len(queryArticlesRes.articles), 1)


  def test_delete_articles(self):
    """
      Tests deleting articles within a specific date range.
    """

    # Populate a set of articles into the database
    numDays = 200
    a1 = Article(
      url = "testUrl1",
      title = "testTitle",
      text = "testText",
      authors = ["testAuthor"],
      date = datetime.now() - timedelta(days = numDays-1),
      topic = "testTopic",
      parentTopic = "testParentTopic",
      topPassage = "testPassage",
      topFact = "testFact",
      imageURL = "testURL",
      polarizationScore = 0.0,
    )
    req1 = SaveArticleRequest(
      article = a1,
    )
    res1 = saveArticle(req1)
    self.assertIsNone(res1.error)

    a2 = Article(
      url = "testUrl2",
      title = "testTitle",
      text = "testText",
      authors = ["testAuthor"],
      date = datetime.now() - timedelta(days = numDays+1),
      topic = "testTopic",
      parentTopic = "testParentTopic",
      topPassage = "testPassage",
      topFact = "testFact",
      imageURL = "testURL",
      polarizationScore = 0.0,
    )
    req2 = SaveArticleRequest(
      article = a2,
    )
    res2 = saveArticle(req2)
    self.assertIsNone(res2.error)

    deletedArticleIds, err = deleteArticles(numDays, False)
    self.assertEqual(deletedArticleIds, [res2.id])
    self.assertIsNone(err)

    deletedArticleIds, err = deleteArticles(numDays, True)
    self.assertEqual(deletedArticleIds, [res2.id])
    self.assertIsNone(err)


  def test_fetch_articles_by_num_days(self):
    """
      Tests fetching articles within a certain date range.
    """

    # Populate a set of articles into the database
    numDays = 200
    a1 = Article(
      url = "testUrl1",
      title = "testTitle",
      text = "testText",
      authors = ["testAuthor"],
      date = datetime.now() - timedelta(days = numDays-1),
      topic = "testTopic",
      parentTopic = "testParentTopic",
      topPassage = "testPassage",
      topFact = "testFact",
      imageURL = "testURL",
      polarizationScore = 0.0,
    )
    req1 = SaveArticleRequest(
      article = a1,
    )
    res1 = saveArticle(req1)
    self.assertIsNone(res1.error)

    a2 = Article(
      url = "testUrl2",
      title = "testTitle",
      text = "testText",
      authors = ["testAuthor"],
      date = datetime.now() - timedelta(days = numDays+1),
      topic = "testTopic",
      parentTopic = "testParentTopic",
      topPassage = "testPassage",
      topFact = "testFact",
      imageURL = "testURL",
      polarizationScore = 0.0,
    )

    req2 = SaveArticleRequest(
      article = a2,
    )
    res2 = saveArticle(req2)
    self.assertIsNone(res2.error)

    articles = fetchArticlesByDateRange(numDays)
    self.assertEqual(articles.articleList[0].id, res1.id)




