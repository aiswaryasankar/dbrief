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
import re

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)

module = "https://tfhub.dev/google/universal-sentence-encoder/4"


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


def process_paragraphs(paragraphs_raw):
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


def get_top_passage_batch(getTopPassageBatchRequest):
  """
    Gets the top passage for all the articles passed in
  """

  # Enforce that a paragraph has at least 2 sentences
  try:
    nltk.data.find('tokenizers/punkt')
  except LookupError:
    nltk.download('punkt')

  embeddingModel = hub.load(module)
  topPassages = []

  for a in getTopPassageBatchRequest.articleList:
    article = clean_text(a.text)
    paragraphs_raw = article.split("\n")
    if article == "" or len(paragraphs_raw) == 0:
      logger.warn("Article text empty for article %s", a.id)
      continue

    paragraphs = process_paragraphs(paragraphs_raw)
    if len(paragraphs) == 0 or len(paragraphs[0]) < 100:
      logger.warn("No paragraphs for article %s", a.id)
      logger.warn(paragraphs)
      logger.warn(article)
      continue

    if len(paragraphs) <= 1:
      topPassages.append(
        ArticlePassage(
          article_id = a.id,
          passage = paragraphs[0],
        )
      )
      continue

    embeddedParagraphs = []
    for paragraph in paragraphs:
      if paragraph != '':
        embeddedParagraphs.append(embeddingModel([paragraph]))
    embeddedParagraphs = np.squeeze(embeddedParagraphs)

    # Create a matrix of paragraphs and compute the dot product between the matrices
    dot_products = np.dot(embeddedParagraphs, embeddedParagraphs.T)
    # Return the top row as the result
    dot_product_sum = sum(dot_products)
    top_passage_index = np.argmax(dot_product_sum)
    # Top passage
    top_passage = paragraphs[top_passage_index]
    topPassages.append(
      ArticlePassage(
        article_id = a.id,
        passage = top_passage,
      )
    )

  return GetTopPassageBatchResponse(
    articlePassages=topPassages,
    error= None,
  )


def get_top_facts_batch(getTopFactsBatchRequest):
  """
    Gets the top facts for all the articles passed in
  """
  try:
    nltk.data.find('tokenizers/punkt')
  except LookupError:
    nltk.download('punkt')

  embeddingModel = hub.load(module)
  topFacts = []

  for a in getTopFactsBatchRequest.articleList:
    article = clean_text(a.text)
    facts = article.split("\n")
    if article == "" or len(facts) == 0 or len(facts[0]) < 100:
      logger.warn("Article text is empty for article %s", a.id)
      logger.info(a.text)
      continue

    facts = nltk.tokenize.sent_tokenize(article)

    if len(facts) == 0 or len(facts[0]) < 100:
      logger.warn("No sentences %s", a.id)
      logger.info(a.text)
      continue

    if len(facts) <= 1:
      topFacts.append(
        ArticleFact(
          article_id = a.id,
          facts = [facts[0]],
        )
      )
      continue

    embeddedFacts = []
    for fact in facts:
      if fact != '':
        embeddedFacts.append(embeddingModel([fact]))
    embeddedFacts = np.squeeze(embeddedFacts)

    # Create a matrix of facts and compute the dot product between the matrices
    dot_products = np.dot(embeddedFacts, embeddedFacts.T)
    # Return the top row as the result
    dot_product_sum = sum(dot_products)
    top_fact_index = np.argmax(dot_product_sum)
    # Top fact
    top_fact = facts[top_fact_index]
    topFacts.append(
      ArticleFact(
        article_id = a.id,
        facts = [top_fact],
      )
    )

  return GetFactsBatchResponse(
    articleFacts=topFacts,
    error= None,
  )


def get_top_passage(getTopPassageRequest):
  """
    Get the top passage from the article and return it
  """
  # Enforce that a paragraph has at least 2 sentences
  try:
    nltk.data.find('tokenizers/punkt')
  except LookupError:
    nltk.download('punkt')

  article = clean_text(getTopPassageRequest.article_text)
  paragraphs_raw = article.split("\n")
  if article == "" or len(paragraphs_raw) == 0:
    logger.warn("Article text empty for article %s", a.id)
    return GetTopPassageResponse(
      passage=[],
      error= ValueError("No paragraphs in article"),
  )

  paragraphs = process_paragraphs(paragraphs_raw)
  if len(paragraphs) == 0:
    logger.warn("No paragraphs for article %s", a.id)
    logger.warn(paragraphs)
    logger.warn(article)
    return GetTopPassageResponse(
      passage=[],
      error= ValueError("No paragraphs in article"),
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
  if not isinstance(dot_products, np.float32) :
    dot_product_sum = sum(dot_products)
  else:
    dot_product_sum = dot_products

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
  article = clean_text(getFactsRequest.article_text)

  try:
    nltk.data.find('tokenizers/punkt')
  except LookupError:
    nltk.download('punkt')

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



