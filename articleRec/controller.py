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
from datetime import datetime


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
    beforeAddDocument = datetime.now()
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
    timeAfterAddDocument = datetime.now()
    logger.info("Time to add document to model %s", timeAfterAddDocument - beforeAddDocument)

  # Get_document_topic batch will return both the topic and the subtopic together
  getDocumentTopicBatchResponse = tpHandler.get_document_topic_batch(
    GetDocumentTopicBatchRequest(
      doc_ids=[saveArticleResponse.id],
      num_topics=1,
    )
  )
  if getDocumentTopicBatchResponse.error != None:
    return PopulateArticleResponse(url=url, id=saveArticleResponse.id, error=str(getDocumentTopicBatchResponse.error))

  topic = getDocumentTopicBatchResponse.documentTopicInfos[0].topic
  parentTopic = getDocumentTopicBatchResponse.documentTopicInfos[0].parentTopic
  logger.info("Document topics")
  logger.info(topic)
  logger.info(parentTopic)

  beforeGetPolarity = datetime.now()
  # Get the polarity of the document from the topic model
  getDocumentPolarityResponse = polarityHandler.get_document_polarity(
    GetDocumentPolarityRequest(
      query=article.text,
      source=None,
    )
  )
  logger.info("Successfully fetched the polarity")
  logger.info(getDocumentPolarityResponse.polarity_score)
  afterGetPolarity = datetime.now()
  logger.info("Time to get polarity %s", afterGetPolarity-beforeGetPolarity)

  isOpinion = False
  if getDocumentPolarityResponse.polarity_score < 0.25 or getDocumentPolarityResponse.polarity_score > 0.75:
    isOpinion = True

  topPassage, topFact = "", ""
  if isOpinion:
    timeBeforeGetPassage = datetime.now()
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
    afterGetPassage = datetime.now()
    logger.info("Time to get passage %s", afterGetPassage-timeBeforeGetPassage)

  else:
    # Get the facts from the document
    # Get the top passage from the document
    timeBeforeGetFact = datetime.now()
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
    timeAfterGetFact = datetime.now()
    logger.info("Time to get fact %s", timeAfterGetFact-timeBeforeGetFact)

  # Update the db with additional data
  updatedArticle = Article(
    id=saveArticleResponse.id,
    topic = topic,
    parentTopic = parentTopic,
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


def article_backfill_controller(articleBackfillRequest):
  """
    This endpoint will function for a few different use cases. First it will be run daily as a way to backfill any missing data in the article database. This includes all fields that are missing. Additionally it can function to update fields even if they were already populated. This would primarily be used for topic regeneration based on an updated model. Thus the request will either take in force_update, as well as a list of fields to update.  If neither are provided it will batch update all fields that are missing.
  """

  articlesToUpdate = []

  if articleBackfillRequest.force_update:
    # Updates the fields in the database for the appropriate values
    fetchAllArticlesRes = fetchAllArticles()
    if fetchAllArticlesRes.error != None:
      logger.error("Failed to fetch all articles for article backfill")
      logger.error(str(fetchAllArticlesRes.error))
      return ArticleBackfillResponse(
        num_updates=0,
        error=fetchAllArticlesRes.error,
      )
    else:
      articlesToUpdate = fetchAllArticlesRes.articleList

  else:
    # Query only the rows that are missing values for the requested fields
    for field in articleBackfillRequest.fields:
      queryArticleResponse = queryArticles(
        QueryArticleRequest(
          field=field,
        )
      )
      if queryArticleResponse.error != None:
        logger.error("Failed to fetch articles for article backfill")
        logger.error(str(queryArticleResponse.error))
        return ArticleBackfillResponse(
          num_updates=0,
          error=queryArticleResponse.error,
        )
      else:
        logger.info("Number of articles to update %s", len(queryArticleResponse.articles))
        articlesToUpdate.extend(queryArticleResponse.articles)

  logger.info("Articles to update %s", len(articlesToUpdate))

  # Based on the field that is requested, it will call the appropriate method
  # Should operate in batch to get the appropriate values back
  if "topic" in articleBackfillRequest.fields or "parent_topic" in articleBackfillRequest.fields:
    getDocumentTopicBatchResponse = tpHandler.get_document_topic_batch(
      GetDocumentTopicRequest(
        doc_ids=[article.id for article in articlesToUpdate],
        num_topics=1,
      )
    )
    if getDocumentTopicBatchResponse.error != None:
      logger.warn("Failed to get topics for batch request")
      return ArticleBackfillResponse(
        num_updates=0,
        error=getDocumentTopicBatchResponse.error,
      )

  # TODO: Implement batch polarity, topic and fact backfill
  # if "polarity" in articleBackfillRequest.fields:
  #   getDocumentPolarityBatchResponse = polarityHandler.get_document_polarity_batch(
  #     GetDocumentPolarityBatchRequest(
  #       queryList=[article.text for article in articlesToUpdate],
  #       source=None,
  #     )
  #   )
  #   if getDocumentPolarityBatchResponse.error != None:
  #     logger.warn("Failed to get polarity for batch request")

  # if "fact" in articleBackfillRequest.fields:
  #   pass


  # if "passage" in articleBackfillRequest.fields:
  #   pass

  # Populate the new fields into the db with an upsert operation
  # This should call the create_or_update article repo function and update the fields that are new
  # You need to make sure that it doesn't erase fields that you haven't passed in this time

  updatedArticles = [ArticleModel(articleId=a.doc_id, topic=a.topic, parent_topic=a.parentTopic) for a in getDocumentTopicBatchResponse.documentTopicInfos]
  logger.info("Number of articles to update %s", len(updatedArticles))

  # TODO: Move this into a repository function
  res = ArticleModel.objects.bulk_update(updatedArticles, ['topic', 'parent_topic'])

  return ArticleBackfillResponse(
    num_updates=len(getDocumentTopicBatchResponse.documentTopicInfos),
    error=None,
  )









