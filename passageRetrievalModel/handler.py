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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_top_passage(getTopPassageRequest):
  """
    Get the top passage from the article and return it
  """
  article = getTopPassageRequest.article_text
  paragraphs = article.split("\n")

  # Enforce that a paragraph has at least 2 sentences
  paragraphs = [paragraph for paragraph in paragraphs if paragraph != '' and len(nltk.tokenize.sent_tokenize(paragraph)) >= 2]
  embeddedParagraphs = []

  module = "https://tfhub.dev/google/universal-sentence-encoder/4"
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
  embeddedFacts = []

  module = "https://tfhub.dev/google/universal-sentence-encoder/4"
  embeddingModel = hub.load(module)

  for fact in facts:
    if fact != '':
      embeddedFacts.append(embeddingModel([fact]))

  embeddedFacts = np.squeeze(embeddedFacts)

  # Create a matrix of facts and compute the dot product between the matrices
  dot_products = np.dot(embeddedFacts, embeddedFacts.T)

  # Return the top row as the result
  dot_product_sum = sum(dot_products)
  logger.info('dot product sum')
  logger.info(dot_product_sum)
  top_fact_indices = np.argpartition(dot_product_sum, -3)[-3:]
  logger.info('top_fact_index')
  logger.info(top_fact_indices)

  # Top fact
  top_facts = [facts[index] for index in top_fact_indices]
  logger.info("top_facts")
  for fact in top_facts:
    logger.info(fact)

  return GetFactsResponse(
    facts=top_facts,
    error= None,
  )
