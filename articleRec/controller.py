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
import constants


def process_rss_feed():
  """
    Will return a list of article urls
  """
  urlList = []

  for entry in constants.rss_feeds:
    feed = feedparser.parse(entry)
    for article in feed.entries:
      try:
        urlList.append(article.links[0].href)
      except Exception as e:
        logger.error("Failed to parse url", extra={"error":e})
        continue

  return urlList


def hydrate_articles_batch(urls):
  """
    Given a list of urls, will return a list of hydrated Article objects
  """
  articleEntities = []

  for url in urls:
    articleEntities.append(hydrate_article(url))

  return articleEntities


def hydrate_article(url):
  """
    Given a url, will return a hydrated Article object
  """

  logger.info(url)
  article = Article(url)
  article.download()
  try:
    article.parse()
  except Exception as e:
    logger.error("Failed to populate article", extra={"url":url, "error": e})

  return article


### Helper Functions
def cron_job_test(request):

  print("Started the cron job")

