from .models import ArticleModel
import logging
from idl import *

"""
  This file will include all the basic database CRUD operations including:
    - Save
    - Query
    - Delete
    - Update
"""

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def saveArticle(SaveArticleRequest):
  """
    Will save the article to the database.  If the article already exists it will update the existing article instead.
  """

  a = SaveArticleRequest.article
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
    articleList.append(
      Article(
        id=article.articleId,
        url=article.url,
        authors=article.author,
        text=article.text,
        title=article.title,
        topic=article.topic,
        parentTopic=article.parentTopic,
        date=article.publish_date,
        imageURL=article.image,
        polarizationScore=article.polarization_score,
        topPassage=article.topPassage,
        topFact=article.topFact,
      )
    )

  return FetchArticlesResponse(
    articleList=articleList,
    error=None,
  )


def fetchArticlesById(articleIds):
  """
    Will fetch articles by the article Id and populate the Article entity
  """
  hydratedArticles = []

  for id in articleIds:
    article = ArticleModel.objects.get(articleId=id)
    hydratedArticles.append(
      Article(
        id=article.articleId,
        url=article.url,
        authors=article.author,
        text=article.text,
        title=article.title,
        topic=article.topic,
        parentTopic=article.parentTopic,
        date=article.publish_date,
        imageURL=article.image,
        polarizationScore=article.polarization_score,
        topPassage=article.topPassage,
        topFact=article.topFact,
      )
    )

  return FetchArticlesResponse(
    articleList=hydratedArticles,
    error=None,
  )


