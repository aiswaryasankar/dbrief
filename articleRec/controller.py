from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from newspaper import Article as ArticleAPI
from newspaper import Config
import feedparser
from .models import ArticleModel
import logging
from logtail import LogtailHandler
import logging
from topicModeling.training import Top2Vec
from .constants import *
from idl import *
from .repository import *
from topicModeling import handler as tpHandler
from polarityModel import handler as polarityHandler
from passageRetrievalModel import handler as passageRetrievalHandler
import multiprocessing as mp


handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)


def fetch_articles_controller(fetchArticlesRequest):
  """
    This function will fetch all the articles from the articleId list provided or fetch all articles in the db if no articleIds are provided.
  """
  if fetchArticlesRequest.articleIds == None or len(fetchArticlesRequest.articleIds) == 0:
    return fetchAllArticles()

  return fetchArticlesById(fetchArticlesRequest.articleIds)


def populate_article(populateArticleRequest):
  """
    PopulateArticles does the following:

      1. Fetch and hydrate all the articles in the RSS feed
      2. Add the document to the topic model with the index of the article in the db
      3. Get the topic for the document from the topic model
      4. Get the subtopic for the document from the topic model
      5. Get the polarity of the article
      6. Get the fact of the article
      7. Get the primary passage of the article
      8. Update db with the additional data
  """

  logger.info("Number of processors: ", mp.cpu_count())
  pool = mp.Pool(mp.cpu_count())

  # Hydrate article
  url = populateArticleRequest.url
  hydrateArticleResponse = hydrate_article_controller(url)
  if hydrateArticleResponse.error != None:
    return PopulateArticleResponse(url=url, id=None, error=str(hydrateArticleResponse.error))

  article=hydrateArticleResponse.article

  # Save to database and fetch article id
  a = Article(
    id=None,
    url=url,
    text=article.text,
    title=article.title,
    date=article.publish_date,
    imageURL=article.top_image,
    authors=article.authors,
    topic=None,
    parentTopic=None,
    polarizationScore=None,
    topPassage=None,
    topFact=None,
  )
  saveArticleResponse = saveArticle(
    SaveArticleRequest(
      article=a,
    )
  )

  # If article is already in the db, don't populate remaining fields
  if saveArticleResponse.error != None:
    return PopulateArticleResponse(url=url, id=None, error=str(ValueError("Failed to save article to database")))

  # If the article is already in the database, its already added to the topic model and thus should not be readded
  if saveArticleResponse.created:
    # Add document to topic model with text and doc id
    addedToTopicModel = tpHandler.add_document(
      AddDocumentRequest(
        documents=[article.text],
        doc_ids=[saveArticleResponse.id],
        tokenizer=None,
        use_embedding_model_tokenizer=None,
      )
    )
    if addedToTopicModel.error != None:
      return PopulateArticleResponse(url=url, id=saveArticleResponse.id, error=str(addedToTopicModel.error))

    logger.info("Added document to the topic model")

  # Get topic for the document from the topic model
  getDocumentTopicResponse = tpHandler.get_document_topic(
    GetDocumentTopicRequest(
      doc_ids=[saveArticleResponse.id],
      reduced=False,
      num_topics=1,
    )
  )
  if getDocumentTopicResponse.error != None:
    return PopulateArticleResponse(url=url, id=saveArticleResponse.id, error=str(getDocumentTopicResponse.error))

  logger.info("Document topic")
  logger.info(getDocumentTopicResponse.topic_num)
  logger.info(getDocumentTopicResponse.topic_score)
  logger.info(getDocumentTopicResponse.topic_word)

  # Get the subtopic for the document from the topic model
  getSubtopicResponse = tpHandler.get_document_topic(
    GetDocumentTopicRequest(
      doc_ids=[saveArticleResponse.id],
      reduced=True,
      num_topics=1,
    )
  )
  if getSubtopicResponse.error != None:
    return PopulateArticleResponse(url=url, id=saveArticleResponse.id, error=str(getSubtopicResponse.error))

  logger.info("Document parent topic")
  logger.info(getSubtopicResponse.topic_num)
  logger.info(getSubtopicResponse.topic_score)
  logger.info(getSubtopicResponse.topic_word)

  # Get the polarity of the document from the topic model
  getDocumentPolarityResponse = polarityHandler.get_document_polarity(
    GetDocumentPolarityRequest(
      query=article.text,
      source=None,
    )
  )
  logger.info("Successfully fetched the polarity")
  logger.info(getDocumentPolarityResponse.polarity_score)

  isOpinion = False
  if getDocumentPolarityResponse.polarity_score < 0.25 or getDocumentPolarityResponse.polarity_score > 0.75:
    isOpinion = True

  topPassage, topFact = "", ""
  if isOpinion:
    # Get the top passage from the document
    getTopPassageResponse = passageRetrievalHandler.get_top_passage(
      GetTopPassageRequest(
        article_text = article.text,
      )
    )
    if getTopPassageResponse.error != None:
      logger.warn("Failed to get top passage for article")
      logger.warn(getTopPassageResponse.error)
    else:
      topPassage=getTopPassageResponse.passage
      logger.info("Successfully extracted the topic passage")

  else:
    # Get the facts from the document
    # Get the top passage from the document
    getFactsResponse = passageRetrievalHandler.get_facts(
      GetFactsRequest(
        article_text = article.text,
      )
    )
    if getFactsResponse.error != None:
      logger.warn("Failed to get facts for article")
      logger.warn(getFactsResponse.error)
    else:
      topFact = getFactsResponse.facts[0]
      logger.info("Successfully extracted the top fact")

  # Update the db with additional data
  updatedArticle = Article(
    id=saveArticleResponse.id,
    topic = getDocumentTopicResponse.topic_word,
    parentTopic = getSubtopicResponse.topic_word,
    url=url,
    text=article.text,
    title=article.title,
    date=article.publish_date,
    imageURL=article.top_image,
    authors=article.authors,
    polarizationScore=getDocumentPolarityResponse.polarity_score,
    topPassage=topPassage,
    topFact=topFact,
  )

  # Save to database and fetch article id
  updateArticleResponse = saveArticle(
    SaveArticleRequest(
      article=updatedArticle,
    )
  )
  if updateArticleResponse.error != None:
    return PopulateArticleResponse(url=url, id=saveArticleResponse.id, error=str(updateArticleResponse.error))

  logger.info("Successfully updated the article")
  return PopulateArticleResponse(url=url, id=saveArticleResponse.id, error=None)


def process_rss_feed():
  """
    Will return a list of article urls
  """
  urlList = []

  for entry in rss_feeds:
    feed = feedparser.parse(entry)
    for article in feed.entries:
      try:
        urlList.append(article.links[0].href)
      except Exception as e:
        logger.error("Failed to parse url", extra={"error":e})
        continue

  return urlList


def hydrate_articles_batch(urls):
  """
    Given a list of urls, will return a list of hydrated Article objects
  """
  articleEntities = []

  for url in urls:
    articleEntities.append(hydrate_article_controller(url))

  return articleEntities


def hydrate_article_controller(url):
  """
    Given a url, will return a hydrated Article object
  """

  user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
  config = Config()
  config.browser_user_agent = user_agent
  config.request_timeout = 15

  logger.info(url)
  article = ArticleAPI(url, config=config)
  article.download()

  try:
    article.parse()

  except Exception as e:
    logger.error("Failed to populate article", extra={"url":url, "error": e})
    return HydrateArticleResponse(
      article=None,
      url=None,
      error=e,
    )

  return HydrateArticleResponse(
    article=article,
    url=article.url,
    error=None,
  )


