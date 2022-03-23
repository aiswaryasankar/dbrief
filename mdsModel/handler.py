"""
  The mdsModel will return a MDS summary of the various articles that are passed into the model.
"""

from idl import *
import numpy as np
import logging
from logtail import LogtailHandler
import os
import openai
import logging
import nltk
import tensorflow_hub as hub

embedding_model = None

openai.api_key = "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"
module = "https://tfhub.dev/google/universal-sentence-encoder/4"

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)


def process_paragraph(paragraphs_raw):
  """
    This function processes the paragraph length
  """
  paragraphs = []
  for paragraph in paragraphs_raw:
    if len(paragraph) > 1500:
      sentences = nltk.tokenize.sent_tokenize(paragraph)
      index = 0
      short_paragraph = ""

      while index < len(sentences):
        while (index < len(sentences) and len(short_paragraph) < 1500) :
          short_paragraph += sentences[index]
          index += 1
        paragraphs.append(short_paragraph)
        short_paragraph = ""
    else:
      paragraphs.append(paragraph)

  paragraphs = [paragraph for paragraph in paragraphs if paragraph != '' and len(nltk.tokenize.sent_tokenize(paragraph)) >= 2]

  paragraphs_original = [paragraph for paragraph in paragraphs_raw if paragraph != '' and len(nltk.tokenize.sent_tokenize(paragraph)) >= 2]

  if len(paragraphs) != len(paragraphs_original):
    logger.info("processed paragraphs: ")
    logger.info([len(paragraph) for paragraph in paragraphs])

  return paragraphs


def get_mds_summary_v2_handler(getMDSSummaryRequest):
  """
    Get the MDS summary using a more standard approach.  This will include practically doing extraction from the legit concatenation of all the article text in order to pick out the most legit sentences from each of the articles. This way you can guarantee that the text actually makes sense, it is constant, it is quick, it is factual "no chance of making things up" and you aren't fing relying on so much GPT credits and get repetitive content out.
  """
  global embedding_model
  if embedding_model == None:
    print("Embedding model is none in add document")
    embedding_model = hub.load(module)

  articles = getMDSSummaryRequest.articles

  # Tokenize everything by sentence? by paragraph? and compute the embeddings and then
  # I think you can test both of the options out and actually go ahead and validate by also printing out all the input article text first to make sure that you are picking out what you thinks makes the most sense. One thing to keep in mind though is that it should be decently cohesive and shouldn't be more than 5 to 6 sentences honestly or else it'll be like a mini article all by itself - so try to either do something with paragraphs or literally pick out the top 6-7 sentences from all the articles combined.

  try:
    nltk.data.find('tokenizers/punkt')
  except LookupError:
    nltk.download('punkt')

  summary = []
  paragraphs = articles.split("\n")

  articleSentences = process_paragraph(paragraphs)

  embeddedSentences = []
  for sent in articleSentences:
    if sent != '':
      embeddedSentences.append(embedding_model([sent]))
  embeddedSentences = np.squeeze(embeddedSentences)

  # Create a matrix of facts and compute the dot product between the matrices
  dot_products = np.dot(embeddedSentences, embeddedSentences.T)
  dot_product_sum = sum(dot_products)

  topSentenceIndices = np.argpartition(dot_product_sum, -1)[-1:]

  topSentences = [articleSentences[index] for index in topSentenceIndices]
  mdsSummary = " ".join(topSentences)

  print("MDS SUMMARY V2")
  print(mdsSummary)

  return GetMDSSummaryResponse(
    summary=mdsSummary,
    error= None,
  )


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



