from rest_framework.decorators import api_view
from rest_framework.response import Response
import datetime
import idl
import logging
from idl import *
from .training import *
from logtail import LogtailHandler
from topicFeed.handler import *
import pandas as pd

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)

topicModelFile = "./modelWeights/polarityModelWeights.bin"


def get_document_polarity(getDocumentPolarityRequest):
  """
    Given the article text and source, it will return the polarity_score and error.

    class GetDocumentPolarityRequest:
      query: Optional[str]
      source: Optional[str]

    class GetDocumentPolarityResponse:
      polarity_score: Optional[float]
      error: Exception
  """

  # Initialize the polarity model
  xlNetPolarityModel = XLNetPredict()

  # Pass in the source and query
  polarity_score = xlNetPolarityModel.predict(getDocumentPolarityRequest.query)
  logger.info("Polarity score")
  logger.info(polarity_score)

  return GetDocumentPolarityResponse(
    polarity_score = polarity_score,
    error = None,
  )


def get_document_polarity_batch(getDocumentPolarityBatchRequest):
  """
    Given the article text and source, it will return the polarity_score and error.

    class GetDocumentPolarityBatchRequest:
      queryList: Optional[List[str]]
      source: Optional[str]

    class GetDocumentPolarityBatchResponse:
      polarity_score: Optional[List[float]]
      error: Exception
  """
  # Initialize the polarity model
  xlNetPolarityModel = XLNetPredict()

  # Pass in the source and query
  articlePolarityList = []
  for article in getDocumentPolarityBatchRequest.articleList:
    query = article.text
    polarity_score = xlNetPolarityModel.predict(query)
    print("Polarity score for article %s", str(article.id))
    print(polarity_score)

    articlePolarity = ArticlePolarity(
      article_id = article.id,
      polarity_score = polarity_score,
    )
    articlePolarityList.append(articlePolarity)

  return GetDocumentPolarityBatchResponse(
    articlePolarities = articlePolarityList,
    error = None,
  )


def get_document_polarity_batch_v2(getDocumentPolarityBatchRequest):
  """
    Speed up using known values for polarity. If the source is known use that to classify otherwise go ahead and let the gods decide.
  """
  articlePolarityList = []
  for article in getDocumentPolarityBatchRequest.articleList:
    print(article.url)
    polarity = parsePolarity(article.url)
    articlePolarity = ArticlePolarity(
      article_id = article.id,
      polarity_score = polarity,
    )
    articlePolarityList.append(articlePolarity)

  return GetDocumentPolarityBatchResponse(
    articlePolarities = articlePolarityList,
    error = None,
  )


def parsePolarity(url):
  """
    Massive switch that returns left or right polarity based on esteemed, reputable sources
  """
  polarity = 0
  if "techcrunch" in url:
    polarity = 0.1
  if "technologyreview" in url:
    polarity = 0.1
  if "arstechnica" in url:
    polarity = .2
  if "venturebeat" in url:
    polarity = .3
  if "vox" in url:
    polarity = .1
  if "wired" in url:
    polarity = .51
  if "theverge" in url:
    polarity = .4
  if "Ieee" in url:
    polarity = .3
  if "cnet" in url:
    polarity = .51
  if "businessinsider" in url:
    polarity = .6
  if "TechSpot" in url:
    polarity = .1
  if "hackernoon" in url:
    polarity = .3
  if "appleinsider" in url:
    polarity = .3
  if "latimes" in url:
    polarity = .2
  if "cnn" in url:
    polarity = .3
  if "huffpost" in url:
    polarity = .4
  if "usatoday" in url:
    polarity = .51
  if "foxnews" in url:
    polarity = .8
  if "breitbart" in url:
    polarity = .9
  if "washingtontimes" in url:
    polarity = .4
  if "thehill" in url:
    polarity = .51
  if "apnews" in url:
    polarity = .45
  if "npr" in url:
    polarity = .45
  if "nytimes" in url:
    polarity = .2
  if "washingtonpost" in url:
    polarity = .6
  if "apnews" in url:
    polarity = .5
  if "nationalreview" in url:
    polarity = .95
  if "dj" in url:
    polarity = .45
  if "bbc" in url:
    polarity = .5
  if "politico" in url:
    polarity = .4
  if "economist" in url:
    polarity = .6

  return polarity

