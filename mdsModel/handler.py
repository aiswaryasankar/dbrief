"""
  The mdsModel will return a MDS summary of the various articles that are passed into the model.
"""

from idl import *
import numpy as np
import logging
from logtail import LogtailHandler
import os
import openai


openai.api_key = "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"

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)


def get_mds_summary_v2_handler(getMDSSummaryRequest):
  """
    Get the MDS summary using a more standard approach
  """
  pass


def get_mds_summary_handler(getMDSSummaryRequest):
  """
    Get the MDS summary and return it
  """
  articles = getMDSSummaryRequest.articles

  # TODO: Actually implement your model here!!!
  # This is just a placeholder for initial launch ease

  prompt = articles[:2000] + "\n\ntl;dr"
  summary = openai.Completion.create(
    engine="davinci",
    prompt=prompt,
    temperature=0.3,
    max_tokens=60,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0
  )

  return GetMDSSummaryResponse(
    summary=summary.choices[0].text,
    error= None,
  )



