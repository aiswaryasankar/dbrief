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
import re
import tensorflow_hub as hub
import numpy as np
import logging
import nltk
from .constants import *

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


def clean_text(text):
  """
    This function will go ahead and perform sanity checks on the text to clean it up of known issues - e.g. Advertisement type words.
  """

  stop_words = ['Advertisement', 'ADVERTISEMENT', 'Read more', 'Read More', "{{description}}", "Close", "CLICK HERE TO GET THE FOX NEWS APP", "Cash4Life", "Share this newsletter", "Sign up", "Sign Me Up", "Enter email address", "Email check failed, please try again", "Your Email Address", "Your Name", "See more", "Listen to this story.", "Save time by listening to our audio articles as you multitask", "OK", "[MUSIC PLAYING]", "Story at a glance", "Show caption", "Hide caption", "Originally broadcast", "You can now listen to FOX news articles!", "FIRST ON FOX", ""]

  num_stop_words = 0
  num_urls = 0
  for word in stop_words:
    text_clean = text.replace(word, "")
    if text != text_clean:
      num_stop_words += 1

  clean_text = re.sub(r'http\S+', '', text_clean)
  clean_text = re.sub(r'\([^)]*\)', '', clean_text)

  if clean_text != text_clean:
    num_urls += 1

  return clean_text


def get_document_cause(getDocumentCauseRequest):
  """
    This is an initial model to get the cause of a document.
  """
  # Embed the original document text
  text = getDocumentCauseRequest.query

  # Filter / clean the input text
  clean_text = clean_text(text)

  # Embed each of the causes
  embeddingModel = hub.load(module)
  embeddedCauses = []
  for cause in causesList:
    if cause != '':
      embeddedCauses.append(embeddingModel([cause]))
  embeddedCauses = np.squeeze(embeddedCauses)


  # Compute the similarity score btwn the two
  embeddedArticle = embeddingModel([clean_text])
  articleEmbeddingMatrix = [embeddedArticle for i in range(len(causesList))]


  # Create a matrix of paragraphs and compute the dot product between the matrices
  dot_products = np.dot(embeddedCauses, articleEmbeddingMatrix.T)

  # Return the top 3 causes
  dot_product_sum = sum(dot_products)
  top_causes_indices = np.argpartition(dot_product_sum, -3)[-3:]

  # Top causes
  top_causes = [causesList[index] for index in top_causes_indices]

  return GetDocumentCausesResponse(
    causeList=top_causes,
    error= None,
  )


