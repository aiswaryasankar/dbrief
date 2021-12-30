from .models import ArticleModel
import logging
from idl import *
from logtail import LogtailHandler

"""
  This file will include all the basic database CRUD operations including:
    - Save
    - Query
    - Delete
    - Update
"""

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)


def saveArticle(saveArticleRequest):
  """
    Will save the article to the database.  If the article already exists it will update the existing article instead.
  """

  a = saveArticleRequest.article
  url = a.url
  title = a.title
  text = a.text
  author = a.authors
  publish_date = a.date
  topic = a.topic
  parentTopic = a.parentTopic
  topPassage = a.topPassage
  topFact = a.topFact
  image= a.imageURL
  polarizationScore = a.polarizationScore
  created = False

  try:
    articleEntry, created = ArticleModel.objects.update_or_create(
      url = url,
      defaults={
        'title': title,
        'text': text,
        'author': author,
        'publish_date': publish_date,
        'topic': topic,
        'parent_topic': parentTopic,
        'top_passage': topPassage,
        'top_fact': topFact,
        'polarization_score': polarizationScore,
        'image': image,
      },
    )
    if created:
      logger.info('saved article', extra={
          "item": {
              "url": url,
              "res": articleEntry,
              "id" : articleEntry.articleId,
              "created": created,
          }
      })
      logger.info("Saved article to the database: ", extra={ "article": articleEntry })
    else:
      logger.info("Updated already existing article")

  except Exception as e:
    logger.warn("Failed to save article to the database", extra= {
      "article": a,
      "error": e,
    })
    print(e)

    return SaveArticleResponse(id=None, error=e, created=created)

  return SaveArticleResponse(id=articleEntry.articleId, error=None, created=created)


def fetchAllArticles():
  """
    Will fetch the entire list of articles from the database and return them as hydrated Article objects
  """

  articleList = []

  for article in ArticleModel.objects.all():
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

      articleList.append(a)
    except Exception as e:
      logger.warn("Failed to fetch article from database", extra={
        "article": article,
        "error": e,
      })
      print(e)

  return FetchArticlesResponse(
    articleList=articleList,
    error=None,
  )


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
