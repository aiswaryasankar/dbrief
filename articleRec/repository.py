from .models import ArticleModel
import logger
from idl import SaveArticleRequest, SaveArticleResponse

"""
  This file will include all the basic database CRUD operations including:
    - Save
    - Query
    - Delete
    - Update
"""


def saveArticle(article=SaveArticleRequest):
  """
    Will save the article to the database
  """

  url = article.url
  title = article.title
  text = article.text
  author = article.authors
  publish_date = article.publish_date

  articleEntry = ArticleModel(
    url = url,
    title = title,
    text = text,
    author = author,
    publish_date = publish_date,
  )
  try:
    response = articleEntry.save()
    logger.info('saved article', extra={
        "item": {
            "url": url,
            "res": response,
            "id": response.id,
        }
    })
    logger.info("Saved article to the database: ", extra={ "article": articleEntry })

  except Exception as e:
    logger.warn("Failed to save article to the database", extra= {
      "article": articleEntry,
      "error": e,
    })

    return SaveArticleResponse(error=e)

  return SaveArticleResponse(id=response.id)

def queryArticles(queryParams):
  """
    Will query for articles based on the provided search parameters
  """
  pass

