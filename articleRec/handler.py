from django.http.response import JsonResponse
from rest_framework.response import Response
import logging
from .controller import *
from .repository import *
from .serializers import *
from logtail import LogtailHandler
from datetime import datetime
import multiprocessing
import os

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


  beforeParallelHydration = datetime.now()
  # Aysynchronously populate all of the topic pages to display on the home page
  sleepLengths = [10 for i in range(50)]
  pool = ThreadPool(processes=50)
  topicPages = pool.map(sleeper, sleepLengths)

  pool.close()
  pool.join()
  afterParallelHydration = datetime.now()

  print("testing parallel")
  print(afterParallelHydration-beforeParallelHydration)

  return HelloWorldResponse(
    name=helloWorldRequest.name
  )

def sleeper(length):
  time.sleep(length)
  print("PID of Parent process is : ", os.getpid())
  print(multiprocessing.current_process().pid)

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

  logger.info("Hydrating %s articles", str(len(urls)))
  print("Hydrating articles: " + str(len(urls)))

  populateArticles = threading.Thread(target=populate_articles_batch, args=(
    PopulateArticlesBatchRequest(
      urls=urls,
    ),))
  populateArticles.start()

  timeAfterPopulateArticle = datetime.now()
  logger.info("Time to populate articles %s", timeAfterPopulateArticle-timeBeforePopulateArticle)

  return PopulateArticlesResponse(
    num_articles_populated=len(urls),
    num_duplicates=0,
    num_errors=0,
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


def delete_articles(deleteArticlesRequest):
  """
    This endpoint will delete articles from the database that are more than numDays old.
  """
  return delete_articles_controller(deleteArticlesRequest)


