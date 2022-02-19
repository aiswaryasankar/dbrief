from rest_framework.decorators import api_view
from rest_framework.response import Response
import datetime
import idl
import logging
from idl import *
from .training import *
from logtail import LogtailHandler
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
  polarity_scores = xlNetPolarityModel.batch_predict(getDocumentPolarityBatchRequest.queryList)
  logger.info("Polarity scores")
  logger.info(polarity_scores)

  return GetDocumentPolarityBatchResponse(
    polarity_score = polarity_scores,
    error = None,
  )


