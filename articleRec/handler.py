from django.http.response import JsonResponse
from rest_framework.response import Response
import logging
from  .controller import *
from .repository import *
from .serializers import *
from logtail import LogtailHandler
from datetime import datetime

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = []
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def hello_world(helloWorldRequest):
  """
    Demo function for testing purposes
  """
  logger.info(helloWorldRequest)
  logger.info(helloWorldRequest.name)
  return HelloWorldResponse(
    name=helloWorldRequest.name
  )


def fetch_articles(fetchArticlesRequest):
  """
    Given a list of articleIds, this will return the entire hydrated article entity in the db for the batch of articles.  If no articleIds are provided, it will return all articles in the database.
  """
  return fetch_articles_controller(fetchArticlesRequest)


def hydrate_article(hydrateArticleRequest):
  """
    Will scrape and hydrate the url passed in and return the result as an Article model object
  """
  return hydrate_article_controller(hydrateArticleRequest.url)


def populate_articles_batch_v1():
  """
    PopulateArticles does the following:

      1. Fetch and hydrate all the articles in the RSS feed
      2. Add the document to the topic model with the index of the article in the db
      3. Get the topic for the document from the topic model
      4. Get the subtopic for the document from the topic model
      5. Get the polarity of the article
      6. Get the fact of the article
      7. Get the primary passage of the article
      8. Update db with the additional data
  """

  urlMap = process_rss_feed()
  numArticlesPopulated, numErrors = 0, 0

  for urlEntry in urlMap:

    url = urlEntry["url"]
    timeBeforePopulateArticle = datetime.now()
    populateArticleResponse = populate_article(
      PopulateArticleRequest(
        url=url,
      )
    )
    timeAfterPopulateArticle = datetime.now()
    logger.info(populateArticleResponse)
    logger.info("Time to populate article %s", timeAfterPopulateArticle-timeBeforePopulateArticle)

    if populateArticleResponse.error != None:
      numErrors+=1
    else:
      numArticlesPopulated+=1

  return PopulateArticlesResponse(
    num_articles_populated=numArticlesPopulated,
    num_errors=numErrors
  )

def populate_articles_batch_v2():
  """
    The v2 handler will call the batch controller instead of hydrating each article individually.
  """
  urlMap = process_rss_feed()
  numArticlesPopulated, numErrors = 0, 0
  urls = [urlEntry["url"] for urlEntry in urlMap]
  timeBeforePopulateArticle = datetime.now()

  populateArticleResponse = populate_articles_batch(
    PopulateArticlesBatchRequest(
      urls=urls,
    )
  )
  timeAfterPopulateArticle = datetime.now()
  logger.info(populateArticleResponse)
  logger.info("Time to populate article %s", timeAfterPopulateArticle-timeBeforePopulateArticle)

  if populateArticleResponse.error != None:
    numErrors+=1
  else:
    numArticlesPopulated+=1

  return PopulateArticlesResponse(
    num_articles_populated=numArticlesPopulated,
    num_errors=numErrors
  )



def populate_article_by_url(populateArticleByUrlRequest):
  """
    Populates a single article based on the request.url
  """
  url = populateArticleByUrlRequest.url
  populateArticleResponse = populate_article(
    PopulateArticleRequest(
      url=url,
    )
  )
  return populateArticleResponse


def article_backfill(articleBackfillRequest):
  """
    This endpoint will function for a few different use cases. First it will be run daily as a way to backfill any missing data in the article database. This includes all fields that are missing. Additionally it can function to update fields even if they were already populated. This would primarily be used for topic regeneration based on an updated model. Thus the request will either take in force_update, as well as a list of fields to update.  If neither are provided it will batch update all fields that are missing.
  """

  return article_backfill_controller(articleBackfillRequest)



