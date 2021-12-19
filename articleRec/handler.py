from numpy.lib.npyio import save
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from newspaper import Article
import feedparser
from .models import ArticleModel
import schedule
import time
# from logtail import LogtailHandler
import logging
import datetime
from topicModeling.training import Top2Vec
from .constants import rss_feeds
from  .controller import *
from .repository import *
import topicModeling.handler as tpHandler
import idl

# handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# logger.addHandler(handler)
# logger.info('LOGTAIL TEST')

@api_view(['GET', 'POST'])
def hello_world(request):
  if request.method == 'POST':
    return Response({"Message": "Got data", "data": request.data})

  return Response({"message": "Hello world lol"})

def fetch_all_articles(request):
  """
    Returns all the articles present in the database
  """
  return fetchAllArticles()


@api_view(['GET'])
def populate_articles_batch(request):
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

  articleText = []
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

@api_view(['GET'])
def populate_article_by_url(request, url):
  """
    Populates a single article based on the request.url
  """
  url = request.GET.get('url', 'https://www.nytimes.com/2021/12/18/world/asia/afghanistan-marja-economy-taliban.html')
  populateArticleResponse = populate_article(
    PopulateArticleRequest(
      url=url,
    )
  )
  return Response()


