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
from topicFeed import handler as topicFeedHandler
from polarityModel import handler as polarityHandler
from passageRetrievalModel import handler as passageRetrievalHandler
import multiprocessing as mp
from datetime import datetime
from newspaper.utils import BeautifulSoup
import threading
from multiprocessing.pool import ThreadPool
import re


handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)


def fetch_articles_controller(fetchArticlesRequest):
  """
    This function will fetch all the articles from the articleId list provided or fetch all articles in the db if no articleIds are provided.
  """

  if fetchArticlesRequest.articleIds != []:
    return fetchArticlesById(fetchArticlesRequest.articleIds)

  elif fetchArticlesRequest.numDays != 0:
    return fetchArticlesByDateRange(fetchArticlesRequest.numDays)

  elif fetchArticlesRequest.articleUrls != '':
    return fetchArticlesByUrl(fetchArticlesRequest.articleUrls)

  else:
    return fetchAllArticles()


def clean_text(text):
  """
    This function will go ahead and perform sanity checks on the text to clean it up of known issues - e.g. Advertisement type words.
  """

  stop_words = ['Advertisement', 'ADVERTISEMENT', 'Read more', 'Read More', "{{description}}", "Close", "CLICK HERE TO GET THE FOX NEWS APP", "Cash4Life", "Share this newsletter", "Sign up", "Sign Me Up", "Enter email address", "Email check failed, please try again", "Your Email Address", "Your Name", "See more"]
  num_stop_words = 0
  num_urls = 0
  for word in stop_words:
    text_clean = text.replace(word, "")
    if text != text_clean:
      num_stop_words += 1

  clean_text = re.sub(r'http\S+', '', text_clean)
  if clean_text != text_clean:
    num_urls += 1

  logger.info("Replaced stop_words " + str(num_stop_words))
  logger.info("Replaced urls " + str(num_urls))
  return clean_text


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
    return PopulateArticleResponse(article=None, url=url, id=None, error=str(hydrateArticleResponse.error))

  article=hydrateArticleResponse.article

    # Hydrate the article date
  if article.publish_date == "" or article.publish_date is None:
    logger.info("Article doesn't have date info using current date %s", datetime.date())
    article.publish_date = datetime.now()

  # Hydrate article author
  if article.authors == []:
    article.authors = [topicFeedHandler.parseSource(url)]

  text = clean_text(article.text)

  # Save to database and fetch article id
  a = Article(
    id=None,
    url=url,
    text=text,
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

  # Failed to save article to database
  if saveArticleResponse.error != None:
    return PopulateArticleResponse(article=None, url=url, id=None, error=str(ValueError("Failed to save article to database")))

  x = threading.Thread(target=hydrateModelOutputsForArticle, args=(
        article, saveArticleResponse.id, url, saveArticleResponse.created
      )
    )
  x.start()

  return PopulateArticleResponse(
    article=article,
    url=url,
    id=saveArticleResponse.id,
    error=None,
  )


def populate_articles_batch(populateArticlesBatch):
  """
    This will hydrate all the articles in batch.
  """
  logger.info("In populate articles batch")
  articleIds, articles = [], []
  num_duplicates = 0

  documents = []

  for url in populateArticlesBatch.urls:

    # First try fetching the article by URL - if present skip since it should already be fully hydrated
    fetchArticlesByUrlRes = fetchArticlesByUrl([url])
    if len(fetchArticlesByUrlRes.articleList) > 0:
      num_duplicates += 1
      continue

    logger.info(url)
    hydrateArticleResponse = hydrate_article_controller(url)
    if hydrateArticleResponse.error != None:
      logger.warn("Failed to hydrate article " + url)
      continue

    article=hydrateArticleResponse.article

    # Hydrate the article date
    if article.publish_date == "" or article.publish_date is None:
      logger.info("Article doesn't have date info using current date")
      article.publish_date = datetime.now()

    # Hydrate article author
    if article.authors == []:
      article.authors = [topicFeedHandler.parseSource(url)]

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

    # create document for document store
    d = {
      'content': article.text,
      'meta': {
        'id': None,
        'url': url,
        'title': article.title,
        'date': article.publish_date,
        'imageURL': article.top_image,
        'authors': " ".join(article.authors).strip(),
        'topic': None,
        'parentTopic': None,
        'polarizationScore': None,
        'topPassage': None,
        'topFact': None,
      }
    }

    # Failed to save article to database
    if saveArticleResponse.error != None:
      logger.warn("Failed to save article to database " + url)
      continue

    elif saveArticleResponse.created:
      d['meta']['id'] = saveArticleResponse.id
      documents.append(d)
      articleIds.append(saveArticleResponse.id)
      articles.append(article.text)

  logger.info("Number of articles to populate: " + str(len(articleIds)))

  if len(articleIds) > 0:
    # Add the articles to the topic model
    addedToTopicModel = tpHandler.add_document(
      AddDocumentRequest(
        documents=articles,
        doc_ids=articleIds,
        tokenizer=None,
      )
    )
    if addedToTopicModel.error != None:
      # How should you most appropriately handle this error?
      logger.warn("Failed to add articles to the index")
      return PopulateArticlesResponse(num_articles_populated=0, num_duplicates=0, num_errors=len(articleIds))


  # For local testing when latency isn't an issue
  # addDocumentsFaissResponse = tpHandler.add_documents_faiss(
  #   AddDocumentsFaissRequest(documents=documents)
  # )
  # if addDocumentsFaissResponse.error != None:
  #   logger.warn("Failed to add docs to FAISS")
  #   logger.warn(addDocumentsFaissResponse.error)
  #   return PopulateArticlesResponse(num_articles_populated=0, num_duplicates=0, num_errors=len(articleIds))

  # addDocumentsElasticSearchResponse = tpHandler.add_documents_elastic_search(
  #   AddDocumentsElasticSearchRequest(documents=documents)
  # )
  # if addDocumentsElasticSearchResponse.error != None:
  #   logger.warn("Failed to add docs to elastic search")
  #   logger.warn(addDocumentsElasticSearchResponse.error)
  #   return PopulateArticlesResponse(num_articles_populated=0, num_duplicates=0, num_errors=len(articleIds))

  # thread to hydrate model calls for articles
  articleBackfill = threading.Thread(target=article_backfill_controller, args=(
    ArticleBackfillRequest(
      force_update= False,
      fields = ["topic", "top_passage", "top_fact", "polarization_score"]
    )))
  articleBackfill.start()

  # thread to add articles to the FAISS document store
  addArticleFAISS = threading.Thread(target=tpHandler.add_documents_faiss, args=(
    AddDocumentsFaissRequest(documents=documents),)
  )
  addArticleFAISS.start()

  # thread to add articles to elastic search document store
  addArticleElasticSearch = threading.Thread(target=tpHandler.add_documents_elastic_search, args=(
    AddDocumentsElasticSearchRequest(documents=documents),)
  )
  addArticleElasticSearch.start()

  res = PopulateArticlesResponse(
    num_articles_populated=len(articleIds),
    num_duplicates=num_duplicates,
    num_errors=0,
  )
  logger.info(res)

  return res



def hydrateModelOutputsForArticle(article, articleId, url, created):
  """
    HydrateModelOutputsForArticle will always be handled asynchronously since it is more time consuming and no live process should wait for it
  """
  # If the article is already in the database, its already added to the topic model and thus should not be re-added
  if created:
    # Add document to topic model with text and doc id
    beforeAddDocument = datetime.now()
    addedToTopicModel = tpHandler.add_document(
      AddDocumentRequest(
        documents=[article.text],
        doc_ids=[articleId],
        tokenizer=None,
        use_embedding_model_tokenizer=None,
      )
    )
    if addedToTopicModel.error != None:
      return PopulateArticleResponse(article=None, url=url, id=articleId, error=str(addedToTopicModel.error))

    logger.info("Added document to the topic model")
    timeAfterAddDocument = datetime.now()
    logger.info("Time to add document to model %s", timeAfterAddDocument - beforeAddDocument)

  # Get_document_topic batch will return both the topic and the subtopic together
  getDocumentTopicBatchResponse = tpHandler.get_document_topic_batch(
    GetDocumentTopicBatchRequest(
      doc_ids=[articleId],
      num_topics=1,
    )
  )
  if getDocumentTopicBatchResponse.error != None:
    return PopulateArticleResponse(article=None, url=url, id=articleId, error=str(getDocumentTopicBatchResponse.error))

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
    id=articleId,
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
    return PopulateArticleResponse(article=article, url=url, id=articleId, error=str(updateArticleResponse.error))

  logger.info("Successfully updated the article")
  print("Finished hydrating model response")
  return PopulateArticleResponse(article=article, url=url, id=articleId, error=None)


def process_rss_feed():
  """
    Will return a list of article urls
  """
  urlMap = []

  for entry in rss_feeds:

    url = entry["url"]
    source = entry["source"]

    feed = feedparser.parse(url)
    for article in feed.entries:
      try:
        urlMap.append({"url":article.links[0].href})
      except Exception as e:
        logger.error("Failed to parse url %s", str(e))
        continue

  return urlMap


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

  try:
    article.download()
    article.parse()
    soup = BeautifulSoup(article.html, 'html.parser')
    dictionary = json.loads("".join(soup.find("script", {"type":"application/ld+json"}).contents))
    date_published = [value for (key, value) in dictionary.items() if key == 'datePublished']
    article_author = [value for (key, value) in dictionary.items() if key == 'author']

    # another method to extract the title
    article_title = [value for (key, value) in dictionary.items() if key == 'headline']


  except Exception as e:
    logger.error("Failed to populate article", extra={"url":url, "error": e})
    return HydrateArticleResponse(
      article=None,
      url=None,
      error=e,
    )

  if article.text == "" or len(article.text) < 25:
    return HydrateArticleResponse(
      article=None,
      url=None,
      error=("Article doesn't have valid text"),
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
  totalUpdates = 0

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

  return backfill(articleBackfillRequest.fields, articlesToUpdate)
  # x = threading.Thread(target=backfill, args=(
  #       articleBackfillRequest.fields,
  #       articlesToUpdate,
  #     )
  #   )
  # x.start()

  # return ArticleBackfillResponse(
  #   num_updates=len(articlesToUpdate),
  #   error=None,
  # )


def backfill(fields, articlesToUpdate):
  # Based on the field that is requested, it will call the appropriate method
  # Should operate in batch to get the appropriate values back
  totalUpdates = 0

  if "topic" in fields or "parent_topic" in fields:
    getDocumentTopicBatchResponse = tpHandler.get_document_topic_batch(
      GetDocumentTopicRequest(
        doc_ids=[article.id for article in articlesToUpdate],
        num_topics=1,
      )
    )
    if getDocumentTopicBatchResponse.error != None:
      logger.warn("Failed to get topics for batch request %s", str(getDocumentTopicBatchResponse.error))
    else:
      updatedArticles = [ArticleModel(articleId=a.doc_id, topic=a.topic, parent_topic=a.parentTopic) for a in getDocumentTopicBatchResponse.documentTopicInfos]

      # TODO: Move this into a repository function
      res = ArticleModel.objects.bulk_update(updatedArticles, ["topic", "parent_topic"])
      totalUpdates += len(updatedArticles)
      logger.info("Updated topic for %s articles", len(updatedArticles))

  if "polarization_score" in fields:
    getDocumentPolarityBatchResponse = polarityHandler.get_document_polarity_batch_v2(
      GetDocumentPolarityBatchRequest(
        articleList=[Article(id=article.id, text=article.text, url=article.url) for article in articlesToUpdate],
        source=None,
      )
    )
    if getDocumentPolarityBatchResponse.error != None:
      logger.warn("Failed to get polarity for batch request")
    else:
      print("Polarity scores")
      print([a.polarity_score for a in getDocumentPolarityBatchResponse.articlePolarities])
      updatedArticles = [ArticleModel(articleId=a.article_id, polarization_score=a.polarity_score) for a in getDocumentPolarityBatchResponse.articlePolarities]
      totalUpdates += len(updatedArticles)

      # TODO: Move this into a repository function
      res = ArticleModel.objects.bulk_update(updatedArticles, ["polarization_score"])
      logger.info("Updated polarity for %s articles", len(updatedArticles))

  if "top_passage" in fields:
    getTopPassageBatchResponse = passageRetrievalHandler.get_top_passage_batch(
      GetTopPassageBatchRequest(
        articleList=[Article(id=article.id, text=article.text) for article in articlesToUpdate]
      )
    )
    if getTopPassageBatchResponse.error != None:
      logger.warn("Failed to get passage for batch request %s", str(getDocumentTopicBatchResponse.error))
    else:
      updatedArticles = [ArticleModel(articleId=a.article_id, top_passage=a.passage) for a in getTopPassageBatchResponse.articlePassages]
      totalUpdates += len(updatedArticles)

      # TODO: Move this into a repository function
      res = ArticleModel.objects.bulk_update(updatedArticles, ["top_passage"])
      logger.info("Updated top passage for %s articles", len(updatedArticles))

  if "top_fact" in fields:
    getTopFactsBatchResponse = passageRetrievalHandler.get_top_facts_batch(
      GetFactsBatchRequest(
        articleList=[Article(id=article.id, text=article.text) for article in articlesToUpdate]
      )
    )
    if getTopFactsBatchResponse.error != None:
      logger.warn("Failed to get topics for batch request %s", str(getDocumentTopicBatchResponse.error))
    else:
      updatedArticles = [ArticleModel(articleId=a.article_id, top_fact=a.facts[0]) for a in getTopFactsBatchResponse.articleFacts]

      # TODO: Move this into a repository function
      res = ArticleModel.objects.bulk_update(updatedArticles, ["top_fact"])
      totalUpdates += len(updatedArticles)
      logger.info("Updated top fact for %s articles", len(updatedArticles))


  # Populate the new fields into the db with an upsert operation
  # This should call the create_or_update article repo function and update the fields that are new
  # You need to make sure that it doesn't erase fields that you haven't passed in this time
  return ArticleBackfillResponse(
    num_updates=totalUpdates,
    error=None,
  )


def delete_articles_controller(deleteArticlesRequest):
  """
    This function will call the repository and delete articles further out than the max num delete day limit.
  """

  deletedArticles, err = deleteArticles(deleteArticlesRequest.num_days, actuallyDelete=False)
  if err != None:
    return DeleteArticlesResponse(num_articles_deleted=0, error=err)


  # Remove articles from document store
  deleteDocumentsFAISSRes = tpHandler.delete_documents_FAISS(
    DeleteDocumentsFaissRequest(
      article_ids=deletedArticles,
    )
  )

  if deleteDocumentsFAISSRes.error != None:
    return DeleteArticlesResponse(
      num_articles_deleted=0,
      error=deleteDocumentsFAISSRes.err,
    )

  # Remove articles from elastic search
  deleteDocumentsElasticSearchRes = tpHandler.delete_documents_elastic_search(
    DeleteDocumentsElasticSearchRequest(
      article_ids=deletedArticles,
    )
  )

  if deleteDocumentsElasticSearchRes.error != None:
    return DeleteArticlesResponse(
      num_articles_deleted=0,
      error=deleteDocumentsElasticSearchRes.err,
    )

  # Remove the articles from the topic model
  deleteDocumentsRes = tpHandler.delete_documents_batch(
    DeleteDocumentsRequest(
      docIds=deletedArticles,
    )
  )

  if err != None:
    return DeleteArticlesResponse(
      num_articles_deleted=deleteDocumentsRes.numArticlesDeleted,
      error=deleteDocumentsRes.error,
    )

  deletedArticles, err = deleteArticles(deleteArticlesRequest.num_days, actuallyDelete=True)
  if err != None:
    return DeleteArticlesResponse(num_articles_deleted=0, error=err)

  return DeleteArticlesResponse(
    num_articles_deleted=len(deletedArticles),
    error=None,
  )

