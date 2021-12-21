from rest_framework.decorators import api_view
from rest_framework.response import Response
import datetime
import idl
import logging
from idl import GetDocumentPolarityRequest, GetDocumentPolarityResponse
from .training import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

topicModelFile = "./modelWeights/polarityModelWeights.bin"


def get_document_polarity(GetDocumentPolarityRequest):
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
  polarity_score = xlNetPolarityModel.predict(GetDocumentPolarityRequest.query)

  return GetDocumentPolarityResponse(
    polarity_score = polarity_score,
    error = None,
  )



