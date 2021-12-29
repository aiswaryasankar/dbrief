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


def get_mds_summary_handler(getMDSSummaryRequest):
  """
    Get the MDS summary and return it
  """
  articles = getMDSSummaryRequest.articles

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



