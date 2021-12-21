from django.http.response import JsonResponse
from rest_framework.response import Response
import logging
from  .controller import *
from .repository import *
from .serializers import *


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def hello_world(helloWorldRequest):
  """
    Demo function for testing purposes
  """
  print(helloWorldRequest)
  print(helloWorldRequest.name)
  return Response(helloWorldRequest)


def fetch_articles(fetchArticlesRequest):
  """
    Given a list of articleIds, this will return the entire hydrated article entity in the db for the batch of articles.  If no articleIds are provided, it will return all articles in the database.
  """
  return fetch_articles(fetchArticlesRequest)


def hydrate_article(hydrateArticleRequest):
  """
    Will scrape and hydrate the url passed in and return the result as an Article model object
  """
  return hydrate_article(hydrateArticleRequest.url)


def populate_articles_batch():
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

  urlList = process_rss_feed()
  numArticlesPopulated, numErrors = 0, 0

  for url in urlList:
    populateArticleResponse = populate_article(
      PopulateArticleRequest(
        url=url,
      )
    )
    if populateArticleResponse.error != None:
      numArticlesPopulated+=1
    else:
      numErrors+=1

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
  return Response(populateArticleResponse)

