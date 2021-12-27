"""
  The passageRetrievalModel will primarily do the following
    1. Split up the article into individual paragraphs
    2. Compute an embedding for each of the paragraphs and store in a matrix
    3. Compute the dot product of the matrices
    4. Select the paragraph with the highest dot product sum as the primary paragraph

    For the first iteration we will be using universal sentence encoders in order to compute the paragraph embeddings. This will allow for consistency with the topic model.
"""

from idl import *
import tensorflow_hub as hub
import numpy as np
import logging
import nltk
from logtail import LogtailHandler

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)

module = "https://tfhub.dev/google/universal-sentence-encoder/4"

def get_top_passage(getTopPassageRequest):
  """
    Get the top passage from the article and return it
  """
  article = getTopPassageRequest.article_text
  paragraphs = article.split("\n")
  if article == "" or len(paragraphs) == 0:
    return GetTopPassageResponse(
      passage=[],
      error= ValueError("Empty article"),
    )

  # Enforce that a paragraph has at least 2 sentences
  facts = nltk.download("punkt")
  paragraphs = [paragraph for paragraph in paragraphs if paragraph != '' and len(nltk.tokenize.sent_tokenize(paragraph)) >= 2]

  if len(paragraphs) == 0:
    return GetTopPassageResponse(
      passage=[],
      error= ValueError("No paragraphs in article"),
  )

  if len(paragraphs) <= 1:
    return GetTopPassageResponse(
      passage=paragraphs[0],
      error= None,
  )

  embeddedParagraphs = []
  embeddingModel = hub.load(module)

  for paragraph in paragraphs:
    if paragraph != '':
      embeddedParagraphs.append(embeddingModel([paragraph]))

  embeddedParagraphs = np.squeeze(embeddedParagraphs)


  # Create a matrix of paragraphs and compute the dot product between the matrices
  dot_products = np.dot(embeddedParagraphs, embeddedParagraphs.T)

  # Return the top row as the result
  dot_product_sum = sum(dot_products)
  logger.info('dot product sum')
  logger.info(dot_product_sum)
  top_passage_index = np.argmax(dot_product_sum)
  logger.info('top_passage_index')
  logger.info(top_passage_index)

  # Top passage
  top_passage = paragraphs[top_passage_index]
  logger.info("top_passage")
  logger.info(top_passage)

  return GetTopPassageResponse(
    passage=top_passage,
    error= None,
  )


def get_facts(getFactsRequest):
  """
    Get facts from the article and return a list of top facts
  """
  article = getFactsRequest.article_text
  facts = nltk.download("punkt")
  facts = nltk.tokenize.sent_tokenize(article)

  if len(facts) == 0 or article == '':
    return GetFactsResponse(
      facts=[],
      error= ValueError("Article text is empty"),
  )
  if len(facts) == 1:
    return GetFactsResponse(
      facts=facts[0],
      error= None,
  )

  embeddedFacts = []
  embeddingModel = hub.load(module)

  for fact in facts:
    if fact != '':
      embeddedFacts.append(embeddingModel([fact]))

  embeddedFacts = np.squeeze(embeddedFacts)

  # Create a matrix of facts and compute the dot product between the matrices
  dot_products = np.dot(embeddedFacts, embeddedFacts.T)

  # Return the top row as the result
  dot_product_sum = sum(dot_products)
  if len(dot_product_sum) >= 3:
    top_fact_indices = np.argpartition(dot_product_sum, -3)[-3:]
  else:
    top_fact_indices = [i for i in range(len(dot_product_sum))]

  # Top fact
  top_facts = [facts[index] for index in top_fact_indices]

  for fact in top_facts:
    logger.info(fact)

  return GetFactsResponse(
    facts=top_facts,
    error= None,
  )



