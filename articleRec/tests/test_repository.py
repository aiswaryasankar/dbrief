from django import test
from django.test import Client
from django.test import TestCase
from idl import *
from repository import *

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
      author = ["testAuthor"],
      publish_date = time.now(),
      topic = "testTopic",
      parentTopic = "testParentTopic",
      topPassage = "testPassage",
      topFact = "testFact",
      image= "testURL",
      polarizationScore = 0.0,
    )
    req = SaveArticleRequest(
      article = a1,
    )
    res = saveArticle(req)
    self.assertIsNone(res.error)
    self.assertEqual(res.id, 1)
    self.assertTrue(res.created)

    a2 = Article(
      url = "testUrl",
      title = "testTitle_updated",
      text = "testText_updated",
      author = ["testAuthor"],
      publish_date = time.now(),
      topic = "testTopic",
      parentTopic = "testParentTopic",
      topPassage = "testPassage",
      topFact = "testFact",
      image= "testURL",
      polarizationScore = 0.0,
    )
    req = SaveArticleRequest(
      article = a2,
    )
    res = saveArticle(req)
    self.assertIsNone(res.error)
    self.assertEqual(res.id, 1)
    self.assertFalse(res.created)


  def test_fetch_articles(self):
    """

    """
    pass



  def test_fetch_all_articles(self):
    """

    """
    pass


def fetchArticlesById(fetchArticlesRequest):
  """
    Will fetch articles by the article Id and populate the Article entity
  """
  hydratedArticles = []
  articleIds = fetchArticlesRequest.articleIds

  for id in articleIds:
    article = ArticleModel.objects.get(articleId=id)
    try:
      a = Article(
          id=article.articleId,
          url=article.url,
          authors=article.author,
          text=article.text,
          title=article.title,
        )

      if article.topic:
        a.topic = article.topic
      if article.parent_topic:
        a.parentTopic = article.parent_topic
      if article.publish_date:
        a.topic = article.publish_date
      if article.image:
        a.imageURL = article.image
      if article.polarization_score:
        a.polarizationScore = article.polarization_score
      if article.top_passage:
        a.topPassage = article.top_passage
      if article.top_fact:
        a.topFact = article.top_fact

      hydratedArticles.append(a)

    except Exception as e:
      logger.warn("Failed to fetch article from database", extra={
        "article": article,
        "error": e,
      })
      return FetchArticlesResponse(
        articleList=hydratedArticles,
        error=e,
      )

  return FetchArticlesResponse(
    articleList=hydratedArticles,
    error=None,
  )


def fetchArticlesByUrl(articleUrls):
  """
    Will fetch articles by the article URL and populate the Article entity
  """
  hydratedArticles = []

  for url in articleUrls:
    try:
      article = ArticleModel.objects.get(url=url)
      a = Article(
          id=article.articleId,
          url=article.url,
          authors=article.author,
          text=article.text,
          title=article.title,
        )

      if article.topic:
        a.topic = article.topic
      if article.parent_topic:
        a.parentTopic = article.parent_topic
      if article.publish_date:
        a.topic = article.publish_date
      if article.image:
        a.imageURL = article.image
      if article.polarization_score:
        a.polarizationScore = article.polarization_score
      if article.top_passage:
        a.topPassage = article.top_passage
      if article.top_fact:
        a.topFact = article.top_fact

      hydratedArticles.append(a)

    except Exception as e:
      logger.warn("Failed to fetch article from database", extra={
        "url": url,
        "error": e,
      })
      return FetchArticlesResponse(
        articleList=[],
        error=e,
      )

  return FetchArticlesResponse(
    articleList=hydratedArticles,
    error=None,
  )


def articleBackfill():
  """

  """
  pass

