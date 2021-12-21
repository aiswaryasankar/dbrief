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
  primary_topic = a.primaryTopic
  sub_topic = a.secondaryTopic
  created = False

  try:
    articleEntry, created = ArticleModel.objects.update_or_create(
      url = url,
      defaults={
        'title': title,
        'text': text,
        'author': author,
        'publish_date': publish_date,
        'primary_topic': primary_topic,
        'sub_topic': sub_topic,
      },
    )
    logger.info('saved article', extra={
        "item": {
            "url": url,
            "res": articleEntry,
            "id" : articleEntry.articleId,
            "created": created,
        }
    })
    logger.info("Saved article to the database: ", extra={ "article": articleEntry })

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
        primaryTopic=article.primaryTopic,
        secondaryTopic=article.secondaryTopic,
        date=article.publish_date,
        imageURL=article.image,
        polarizationScore=article.polarizationScore,
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
        primaryTopic=article.primary_topic,
        secondaryTopic=article.sub_topic,
        date=article.publish_date,
        imageURL=article.image,
        polarizationScore=article.polarizationScore,
      )
    )

  return FetchArticlesResponse(
    articleList=hydratedArticles,
    error=None,
  )


