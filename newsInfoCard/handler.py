"""
  This service is primarily responsible for creating the NewsInfo cards.
"""

import logging
from articleRec import handler as articleRecHandler
from mdsModel import handler as mdsHandler
from topicFeed import handler as topicFeedHandler
from .repository import *
from topicModeling import handler as tpHandler
from mdsModel.handler import *
from datetime import datetime
import idl
import threading
import random
from multiprocessing.pool import ThreadPool, Pool

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)



def createNewsInfoCard(createNewsInfoCardRequest):
  """
    This function will create a newsInfoCard.

      1. Check if article is passed in or the URL, if article pull needed content
      2. Query related articles
      3. Generate topic
      4. If a polarized topic, call CreateOpinionCard for left and right articles
      5. Save the newsInfoCard with OpinionCards or list of links
  """

  if createNewsInfoCardRequest.article != None:
    article = createNewsInfoCardRequest.article

  elif createNewsInfoCardRequest.articleURL != None:
    # Fetch the article
    fetchArticleResponse = articleRecHandler.fetch_articles(
      FetchArticlesRequest(
        articleUrls=[createNewsInfoCardRequest.articleURL]
      )
    )
    if fetchArticleResponse.error != None:
      logger.warn("Failed to fetch article, hydrating the article")

    # If article doesn't exist populate the article
    populateArticleResponse = articleRecHandler.populate_article_by_url(
      PopulateArticleRequest(
        url=createNewsInfoCardRequest.articleURL
      )
    )
    if populateArticleResponse.error != None:
      return CreateNewsInfoCardResponse(
        newsInfoCard=None,
        error = populateArticleResponse.error
      )
    article = populateArticleResponse.article

  # Query for related articles
  queryArticlesResponse = tpHandler.query_documents(
    QueryDocumentsRequest(
      query=article.text,
      num_docs=8,
      use_index=True,
      ef=200,
      return_docs=False,
    )
  )
  if queryArticlesResponse.error != None:
    return CreateNewsInfoCardResponse(
      newsInfoCard=None,
      error = queryArticlesResponse.error
    )

  # Fetch the corresponding articles from db
  fetchArticlesResponse = articleRecHandler.fetch_articles(
    FetchArticlesRequest(
      articleIds = queryArticlesResponse.doc_ids
    )
  )
  if fetchArticlesResponse.error != None:
    return CreateNewsInfoCardResponse(
      newsInfoCard=None,
      error = fetchArticlesResponse.error
    )

  articles = fetchArticlesResponse.articleList
  leftArticles = [article for article in articles if article.polarizationScore < .5]
  rightArticles = [article for article in articles if article.polarizationScore >= .5]
  rightOpinionCardUUID, leftOpinionCardUUID = 0, 0

  # Create the right opinion card
  rightOpinionCardResponse = createOpinionCard(
    CreateOpinionCardRequest(
      articleList = rightArticles,
      polarity = 1,
    )
  )
  if rightOpinionCardResponse.error != None:
    logger.warn("Failed to create right opinion card")
  else:
    rightOpinionCardUUID = rightOpinionCardResponse.opinionCard.uuid

  # Create the left opinion card
  leftOpinionCardResponse = createOpinionCard(
    CreateOpinionCardRequest(
      articleList = leftArticles,
      polarity = 0,
    )
  )
  if leftOpinionCardResponse.error != None:
    logger.warn("Failed to create left opinion card")
  else:
    leftOpinionCardUUID = leftOpinionCardResponse.opinionCard.uuid

  # Save the news info card
  # TODO: handle the non political news info card flow
  # TODO: add summarization to articleModel
  source = topicFeedHandler.parseSource(article.url)

  createNewsInfoCardRes = createNewsInfoCardRepo(
    CreateNewsInfoCardRepoRequest(
      url = article.url,
      title = article.title,
      summary = article.text,
      author = article.authors,
      publish_date = article.date,
      image = article.imageURL,
      topic = article.topic,
      source = source,
      is_political = True,
      left_opinion_card_UUID = leftOpinionCardUUID,
      right_opinion_card_UUID = rightOpinionCardUUID,
      article_url_list = "",
      article_title_list = "",
    )
  )
  if createNewsInfoCardRes.error != None:
    return CreateNewsInfoCardResponse(
      newsInfoCard = None,
      error = createNewsInfoCardRes.error
    )

  return CreateNewsInfoCardResponse(
    newsInfoCard=createNewsInfoCardRes.newsInfoCard,
    error= None,
  )


def createOpinionCard(createOpinionCardRequest):
  """
    Creates an opinion card with a given list of articles
  """

  articles = " " .join([article.text for article in createOpinionCardRequest.articleList])

  # Generate a summary from all of the articles
  getMDSSummaryResponseV2 = mdsHandler.get_mds_summary_v3_handler(
      GetMDSSummaryAndTitleRequest(
        articles=articles,
        include_title=False,
      )
    )
  if getMDSSummaryResponseV2.error != None:
    return CreateOpinionCardResponse(
      opinionCard = None,
      error = getMDSSummaryResponseV2.error
    )

  # Create the opinion card
  createOpinionCardRes = createOpinionCardRepo(
    CreateOpinionCardRequest(
      summary=getMDSSummaryResponseV2.summary,
      articleList=createOpinionCardRequest.articleList,
      polarity=createOpinionCardRequest.polarity
    )
  )
  if createOpinionCardRes.error != None:
    logger.warn("Failed to save opinion card")
    return createOpinionCardRes

  return CreateOpinionCardResponse(
    opinionCard = createOpinionCardRes.opinionCard,
    error = None
  )



def createNewsInfoCardBatch(createNewsInfoCardBatchRequest):
  """
    Creates a batch of news info cards.
  """
  newsInfoCards = []
  # Hydrate a batch of news info cards
  if len(createNewsInfoCardBatchRequest.articleList) > 0:
    for i, article in createNewsInfoCardBatchRequest.articleList:
      logger.info("Creating newsInfoCard " + str(i) + " for article " + str(article.url))

      createOpinionCardResponse = createNewsInfoCard(
        CreateNewsInfoCardRequest(
          article = article,
        )
      )
      if createOpinionCardResponse.error != None:
        logger.warn("Failed to create newsInfoCard " + str(i) + " for article " + str(article.url))
        continue
      else:
        newsInfoCards.append(createOpinionCardResponse.newsInfoCard)
        logger.info("Created newsInfoCard " + str(i) + " for article " + str(article.url))

  if len(createNewsInfoCardBatchRequest.articleUrls) > 0:
    for i, url in createNewsInfoCardBatchRequest.articleUrls:
      logger.info("Creating newsInfoCard " + str(i) + " for article " + str(url))

      createOpinionCardResponse = createNewsInfoCard(
        CreateNewsInfoCardRequest(
          articleURL = url,
        )
      )
      if createOpinionCardResponse.error != None:
        logger.warn("Failed to create newsInfoCard " + str(i) + " for article " + str(url))
        continue
      else:
        newsInfoCards.append(createOpinionCardResponse.newsInfoCard)
        logger.info("Created newsInfoCard " + str(i) + " for article " + str(url))

  return CreateNewsInfoCardBatchResponse(
    newsInfoCards=newsInfoCards,
    error = None,
  )



def fetchNewsInfoCardBatch(fetchNewsInfoCardBatchRequest):
  """
    Fetch a batch of news info cards.
  """
  # Fetch all news info cards ordered by date according to the offset and limit
  fetchNewsInfoCardsBatchRes = fetchNewsInfoCardBatchRepo(
    FetchNewsInfoCardBatchRequest(
      offset = fetchNewsInfoCardBatchRequest.offset,
      pageSize = fetchNewsInfoCardBatchRequest.pageSize,
    )
  )
  if fetchNewsInfoCardsBatchRes.error != None:
    return FetchNewsInfoCardBatchResponse(
      newsInfoCards=None,
      error = fetchNewsInfoCardsBatchRes.error
    )

  return FetchNewsInfoCardBatchResponse(
    newsInfoCards=fetchNewsInfoCardsBatchRes.newsInfoCards,
    error=None
  )





