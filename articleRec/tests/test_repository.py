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

  def test_save_article_create(self):
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
    res = saveArticle(req)
    self.assertIsNone(res.error)
    self.assertEqual(res.id, 2)
    self.assertTrue(res.created)

    a2 = Article(
      id = 2,
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

    res = saveArticle(req)
    self.assertIsNone(res.error)
    self.assertEqual(res.id, 2)
    self.assertFalse(res.created)

    # Fetch the article from the database and check it has been updated appropriately
    fetchedArticleRes = fetchArticlesById(
      FetchArticlesRequest(
        articleIds=[2]
      )
    )
    self.assertIsNone(fetchedArticleRes.error)
    logger.info(fetchedArticleRes.articleList)
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



  def test_article_backfill_force(self):
    """
      Test out force updating all the topics in the database right now
    """



  def test_article_backfill(self):
    """
      Test out backfilling only empty values in the database
    """
    # Populate 2 articles in the database, one without a topic and one with a topic


    # Pass in a request for topic with force_update set to false


    # Update all values
    pass


