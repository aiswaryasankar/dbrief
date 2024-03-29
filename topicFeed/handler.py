"""
  This service is primarily responsible for serving all the content for the topic pages. This service will handle the remaining calls to generate the topic model.  This includes GetTopicPageByURL, GetTopicPageByArticleId, GetTopicPageBySearchString, GetTopicPageByTopicId.  It will also surface the side bars for WhatsHappening, GetRecommendedTopicsForUser and GetTopicsYouFollow.  The 4 methods that handle populating the page will essentially take care of mapping the search query to the appropriate form and then fetching all the content necessary for the topic page. Each will call the same base function to hydrate the information.
"""

import logging
from articleRec import handler as articleRecHandler
from articleRec.repository import fetchArticlesByDateRange
from topicFeed.repository import *
from topicModeling import handler as tpHandler
from mdsModel.handler import *
from datetime import datetime
import idl
import threading
import random
from multiprocessing.pool import ThreadPool, Pool
from .utils import *

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)



def getTopicPage(getTopicPageRequest):
  """
    This function will map the request params of url, articleID, topic string or search string to the appropriate field and pass it to the controller to hydrate the page appropriately. It will execute the following in order to hydrate the TopicPage struct:

      1. QueryDocuments using the text of the article
      2. Fetch all articles queried from articleRec using the articleIds
      3. GetTitleSummaryForSearch in order to fetch the title for the articles
      4. GetMDS to get the MDS for the articles
      5. Optionally query for the key facts and passages if not stored in the DB already
      6. Handle pagination of the facts and opinion results

    Determine whether or not to display a timeline or the opinion format.
  """
  logger.info("get topic page request")
  logger.info(getTopicPageRequest)

  # Check if the page is cached to begin with
  fetchTopicPageByTopicRes = fetchTopicPage(
      fetchTopicPageRequest=FetchTopicPageRequest(
        topic=getTopicPageRequest.topicName,
        topicPageId=getTopicPageRequest.topicId,
        topArticleId=getTopicPageRequest.articleId,
      )
    )
  logger.info("Fetch topic page cached: ")
  logger.info(fetchTopicPageByTopicRes)
  if fetchTopicPageByTopicRes.error != None and fetchTopicPageByTopicRes.topic_page ==  None:
    logger.warn("Failed to hydrate topic page: " + str(fetchTopicPageByTopicRes.error))
  else:
    return GetTopicPageResponse(
      topic_page = fetchTopicPageByTopicRes.topic_page,
      error = None,
    )

  startTime = datetime.now()

  if getTopicPageRequest.url != "":
    # Try to fetch the article if already in db
    articleId = -1
    fetchArticlesResponse = articleRecHandler.fetchArticles(
      FetchArticlesRequest(
        articleUrls=[getTopicPageRequest.url]
      )
    )
    if fetchArticlesResponse.error != None or len(fetchArticlesResponse.articleList) == 0:
      # Populate the article which will hydrate the critical fields and populate the remaining model based fields async
      populateArticleRes = articleRecHandler.populate_article_by_url(
            PopulateArticleRequest(
              url = getTopicPageRequest.url,
            )
          )
      if populateArticleRes.error != None:
        return GetTopicPageResponse(
          topic_page=None,
          error=str(populateArticleRes.error)
        )
      else:
        article = populateArticleRes.article
        articleId = populateArticleRes.id
        text = populateArticleRes.article.text

    else:
      article = fetchArticlesResponse.articleList[0]
      articleId = fetchArticlesResponse.articleList[0].id
      text = article.text

  if getTopicPageRequest.text and getTopicPageRequest.text != "":
    article = None
    articleId = -1
    text = getTopicPageRequest.text.replace('"','\\"')

    # Get the top article based on that text
    queryDocumentsResponse = tpHandler.query_documents(
      QueryDocumentsRequest(
        query=text,
        num_docs=1,
        return_docs=False,
        ef=200,
        use_index=True,
      )
    )
    if queryDocumentsResponse.error != None or len(queryDocumentsResponse.doc_ids) < 1:
      return GetTopicPageResponse(
        topic_page=None,
        error=str(queryDocumentsResponse.error)
      )

    articleId = queryDocumentsResponse.doc_ids[0]
    fetchArticlesResponse = articleRecHandler.fetchArticles(
      fetchArticlesRequest= FetchArticlesRequest(
        articleIds=[articleId],
      )
    )
    if fetchArticlesResponse.error != None or len(fetchArticlesResponse.articleList) == 0:
      # Hydrate the article if not in db and rewrite
        return GetTopicPageResponse(
          topic_page=None,
          error=str(fetchArticlesResponse.error),
        )
    text = fetchArticlesResponse.articleList[0].text
    article = fetchArticlesResponse.articleList[0]

  if getTopicPageRequest.topicName != "":
    # Get top article for the topic id
    # First query the database for the topic and then use the topic string to query the articles
    beforeFetchTopicInfos = datetime.now()
    fetchTopicInfoBatchResponse = tpHandler.fetch_topic_infos_batch(
      FetchTopicInfoBatchRequest(
        topicNames = [getTopicPageRequest.topicName]
      )
    )
    if fetchTopicInfoBatchResponse.error != None or len(fetchTopicInfoBatchResponse.topics) < 1:
      return GetTopicPageResponse(
        topic_page=None,
        error= str(fetchTopicInfoBatchResponse.error)
      )
    afterFetchTopicInfos = datetime.now()
    logger.info("Time to fetch topicInfos %s", str(afterFetchTopicInfos-beforeFetchTopicInfos))
    logger.info("Topics fetched")
    logger.info(fetchTopicInfoBatchResponse.topics)
    beforeQueryDocuments = datetime.now()
    queryDocumentsResponse = tpHandler.query_documents(
      QueryDocumentsRequest(
        query=fetchTopicInfoBatchResponse.topics[0].TopicName,
        num_docs=1,
        return_docs=False,
        ef=200,
        use_index=True,
      )
    )
    if queryDocumentsResponse.error != None or len(queryDocumentsResponse.doc_ids) < 1:
      return GetTopicPageResponse(
        topic_page=None,
        error=str(queryDocumentsResponse.error)
      )

    afterQueryDocuments = datetime.now()
    logger.info("Time to populate query documents %s", str(afterQueryDocuments-beforeQueryDocuments))

    beforeFetchArticles = datetime.now()
    articleId = queryDocumentsResponse.doc_ids[0]
    fetchArticlesResponse = articleRecHandler.fetchArticles(
      fetchArticlesRequest= FetchArticlesRequest(
        articleIds=[articleId],
      )
    )
    if fetchArticlesResponse.error != None or len(fetchArticlesResponse.articleList) == 0:
      # Hydrate the article if not in db and rewrite
        return GetTopicPageResponse(
          topic_page=None,
          error=str(fetchArticlesResponse.error),
        )
    text = fetchArticlesResponse.articleList[0].text
    article = fetchArticlesResponse.articleList[0]
    afterFetchArticles = datetime.now()
    logger.info("Time to populate fetch articles %s", str(afterFetchArticles-beforeFetchArticles))

  if getTopicPageRequest.articleId != 0:
    fetchArticlesResponse = articleRecHandler.fetchArticles(
      fetchArticlesRequest= FetchArticlesRequest(
        articleIds=[getTopicPageRequest.articleId],
      )
    )
    if fetchArticlesResponse.error != None or len(fetchArticlesResponse.articleList) == 0:
      # Hydrate the article if not in db and rewrite
        return GetTopicPageResponse(
          topic_page=None,
          error=str(fetchArticlesResponse.error),
        )

    else:
      article = fetchArticlesResponse.articleList[0]
      articleId = fetchArticlesResponse.articleList[0].id
      text = article.text


  logger.info("Article")
  logger.info(article)
  logger.info("Article ID")
  logger.info(articleId)
  logger.info("Article text")
  logger.info(article.text)

  beforeQueryDocumentsP2 = datetime.now()
  # Query for top documents based on the article text
  queryDocumentsResponse = tpHandler.query_documents(
    QueryDocumentsRequest(
      query=text,
      num_docs=20,
      return_docs=False,
      use_index=True,
      ef=200,
    )
  )
  if queryDocumentsResponse.error != None:
    return GetTopicPageResponse(topic_page=None, error=str(queryDocumentsResponse.error))

  afterQueryDocumentsP2 = datetime.now()
  logger.info("Time to populate queryDocumentsV2 %s", str(afterQueryDocumentsP2-beforeQueryDocumentsP2))
  logger.info("query doc response")
  logger.info(queryDocumentsResponse)

  # Fetch the related articles from the database
  beforeFetchArticlesP2 = datetime.now()
  fetchArticlesResponse = articleRecHandler.fetchArticles(
    FetchArticlesRequest(
      articleIds= queryDocumentsResponse.doc_ids,
    )
  )
  if fetchArticlesResponse.error != None:
    return GetTopicPageResponse(topic_page=None, error=str(fetchArticlesResponse.error))

  afterFetchArticlesP2 = datetime.now()
  logger.info("Time to populate FetchArticlesP2 %s", str(afterFetchArticlesP2-beforeFetchArticlesP2))

  # Get the topic from the primary article
  beforeGetDocumentTopicBatchP2 = datetime.now()
  getDocumentTopicBatchResponse = tpHandler.get_document_topic_batch(
    GetDocumentTopicBatchRequest(
      doc_ids=[int(articleId)],
      num_topics=1
    )
  )
  if getDocumentTopicBatchResponse.error != None or len(getDocumentTopicBatchResponse.documentTopicInfos) < 1:
    return GetTopicPageResponse(topic_page=None, error=str(getDocumentTopicBatchResponse.error))

  afterGetDocumentTopicBatchP2 = datetime.now()
  logger.info("Time to populate get document topic batch p2 %s", str(afterGetDocumentTopicBatchP2-beforeGetDocumentTopicBatchP2))
  topicName = getDocumentTopicBatchResponse.documentTopicInfos[0].topic
  topicID = None

  beforeFetchTopicInfosP2 = datetime.now()
  fetchTopicInfoBatchResponse = tpHandler.fetch_topic_infos_batch(
    FetchTopicInfoBatchRequest(
      topicNames=[topicName],
    )
  )
  if fetchTopicInfoBatchResponse.error != None or len(fetchTopicInfoBatchResponse.topics) < 1:
    # Soft failure since this isn't as critical
    logger.info("Failed to fetch topic id for topic " + topicName)
  else:
    topicID = fetchTopicInfoBatchResponse.topics[0].TopicID

  afterFetchTopicInfosP2 = datetime.now()
  logger.info("Time to populate fetchTopicInfosP2 %s", str(afterFetchTopicInfosP2-beforeFetchTopicInfosP2))

  # GetMDS to get the MDS for the articles
  articles = ""
  topImageUrl = ""
  urls = ", ".join([article.url for article in fetchArticlesResponse.articleList])
  titles = ", ".join([article.title for article in fetchArticlesResponse.articleList])
  logger.info("titles: " + str(titles))

  for a in fetchArticlesResponse.articleList:
    articles += a.text
    if a.imageURL != "":
      topImageUrl = a.imageURL

  beforeMds = datetime.now()
  getMDSSummaryResponse = get_mds_summary_v2_handler(
    GetMDSSummaryRequest(
      articles=articles
    )
  )
  if getMDSSummaryResponse.error != None:
    return GetTopicPageResponse(topic_page=None, error=str(getMDSSummaryResponse.error))

  afterMds = datetime.now()
  logger.info("Time to populate MDS %s", str(afterMds-beforeMds))

  logger.info("MDS SUMMARY")
  logger.info(getMDSSummaryResponse.summary)

  beforeMDSV2 = datetime.now()
  if getTopicPageRequest.savePage:
    getMDSSummaryResponseV2 = get_mds_summary_v3_handler(
      GetMDSSummaryAndTitleRequest(
        articles=articles,
        include_title=True,
      )
    )
    title = getMDSSummaryResponseV2.title
    if getMDSSummaryResponseV2.error != None:
      return GetTopicPageResponse(topic_page=None, error=str(getMDSSummaryResponseV2.error))

  else:
    getMDSSummaryResponseV2 = get_mds_summary_v2_handler(
      GetMDSSummaryRequest(
        articles=articles
      )
    )
    title = article.title
    if getMDSSummaryResponseV2.error != None:
      return GetTopicPageResponse(topic_page=None, error=str(getMDSSummaryResponseV2.error))

  afterMdsV2 = datetime.now()
  logger.info("Time to populate MDS V2 %s", str(afterMdsV2-beforeMDSV2))

  logger.info("MDS SUMMARY V2")
  logger.info(getMDSSummaryResponseV2.summary)

  logger.info("Original title: " + str(article.title))
  logger.info("Generated title: " + str(title))
  facts = []
  passages = []

  for a in fetchArticlesResponse.articleList:
    if a.authors is not None and a.authors != "[]":
      author = a.authors.split(",")[0].replace("[", "").replace('\'', "").replace("]", "")
    else:
      author = parseSource(article.url)

    if a.date == "":
      a.date = datetime.now()

    source = parseSource(a.url)
    logger.info("URL %s and source %s", a.url, source)
    if a.topFact != None and len(a.topFact) > 5 and a.topFact != "":
      facts.append(
        Fact(
          Quote= Quote(
            Text=a.topFact,
            SourceName=source,
            Author=author,
            SourceURL=a.url,
            ArticleID=a.id,
            Polarization=0,
            Timestamp=a.date,
            ImageURL=a.imageURL,
          )
        )
      )

    if a.topPassage != None and len(a.topPassage) > 5 and a.topPassage != "":
      passages.append(
        Opinion(
          Quote= Quote(
            Text=a.topPassage,
            SourceName=source,
            Author=author,
            SourceURL=a.url,
            ArticleID=a.id,
            Polarization=a.polarizationScore,
            Timestamp=a.date,
            ImageURL=a.imageURL,
          )
        )
      )

  isTimeline = True
  if random.random() < .5:
    isTimeline = False

  topic_page = TopicPage(
    Title = title,
    MDSSummary = getMDSSummaryResponseV2.summary,
    Facts = facts,
    Opinions = passages,
    TopArticleID = int(articleId),
    IsTimeline = isTimeline,
    TopicID = topicID,
    TopicName = topicName,
    ImageURL = topImageUrl,
    CreatedAt = datetime.now(),
  )
  logger.info("TOPIC PAGE")
  logger.info(topic_page)
  endTime = datetime.now()
  logger.info("Time to populate topic page %s", endTime - startTime)

  if getTopicPageRequest.savePage:
    saveTopicPageRes = saveTopicPage(
      SaveTopicPageRequest(
        topic=topicName,
        topicId=topicID,
        summary=getMDSSummaryResponseV2.summary,
        title=title,
        imageURL=topImageUrl,
        urls=urls,
        topArticleId=int(articleId),
        isTimeline=isTimeline,
      )
    )
    if saveTopicPageRes.error != None:
      logger.warn("Failed to save topic page for topic: " + str(topicName))
      logger.warn(saveTopicPageRes.error)

  return GetTopicPageResponse(
    topic_page=topic_page,
    error=None,
  )


def whatsHappeningV2(whatsHappeningRequest):
  """
    This version of whats happening takes the time into account and only returns the top x articles for the given day.
    It will first fetch the latest articles within the last 2 days from the db and then choose a few randomly / possibly ones that relate to the top topics.
  """
  # Get most recent articles
  fetchArticlesByDateRangeResponse = articleRecHandler.fetch_articles(
    FetchArticlesRequest(
      numDays=2,
    )
  )

  # Shuffle up the article list to allow for diversity
  random.shuffle(fetchArticlesByDateRangeResponse.articleList)

  articleInfo = []
  for article in fetchArticlesByDateRangeResponse.articleList[:8]:
    articleInfo.append(
      ArticleInfo(
        Id= article.id,
        Title=article.title,
        TopicName=article.topic,
        ImageURL=article.imageURL,
        TopPassage=article.topPassage,
      )
    )

  return WhatsHappeningResponse(
    articles=articleInfo,
    error = None,
  )


def whatsHappening(whatsHappeningRequest):
  """
    This endpoint will get a list of the top x topics, select the top article per topic to include in the side bar for whatsHappening and then hydrate each of the articles into the appropriate whatsHappeningResponse struct.
  """
  getTopicsResponse = tpHandler.get_topics(
    GetTopicsRequest(
      num_topics=5,
      reduced = False,
    )
  )
  if getTopicsResponse.error != None:
    return WhatsHappeningResponse(
      articles=[],
      error=str(getTopicsResponse.error)
    )
  logger.info("Topics")
  logger.info(getTopicsResponse.topic_words)
  articleIds = []

  # For each topic returned, get the top article for the topic
  for topic in getTopicsResponse.topic_nums:
    searchDocumentsByTopicResponse = tpHandler.search_documents_by_topic(
      SearchDocumentsByTopicRequest(
        topic_num = topic,
        num_docs=4,
      )
    )
    # No hard failure if one of the search requests fails
    if searchDocumentsByTopicResponse.error != None:
      logger.warn("Failed to get documents for topic")
      continue

    articleIds.extend(searchDocumentsByTopicResponse.doc_ids)

  # Fetch all the articles from the database
  fetchArticlesByIdResponse = articleRecHandler.fetchArticles(
    FetchArticlesRequest(
      articleIds=articleIds,
    )
  )
  if fetchArticlesByIdResponse.error != None:
    return WhatsHappeningResponse(
      articles=[],
      error=str(fetchArticlesByIdResponse.error)
    )

  # Shuffle up the article list to allow for diversity
  random.shuffle(fetchArticlesByIdResponse.articleList)
  articleInfo = []
  for article in fetchArticlesByIdResponse.articleList[:8]:
    articleInfo.append(
      ArticleInfo(
        Id= article.id,
        Title=article.title,
        TopicName=article.topic,
        ImageURL=article.imageURL,
        TopPassage=article.topPassage,
      )
    )

  return WhatsHappeningResponse(
    articles=articleInfo,
    error = None,
  )


def fetchTopicPageByTopic(fetchTopicPageByTopicRequest):
  """
    Fetches the latest topic page by topic.
  """
  fetchTopicPageRes = fetchTopicPage(
    fetchTopicPageByTopicRequest
  )

  if fetchTopicPageRes.error != None:
    return FetchTopicPageResponse(
      topic_page=None,
      error=fetchTopicPageRes.error,
    )

  return fetchTopicPageRes


def hydrateTopicPages(hydrateTopicPagesRequest):
  """
    This will fetch all the topics in the database and hydrate the corresponding topic pages for those topics into the database as well.  Ideally there will only be 5 days of topics in the db at a time.
  """

  # Fetch all topics from the database
  fetchAllTopicsRes = tpHandler.fetch_all_topics()
  if fetchAllTopicsRes.error != None:
    return HydrateTopicPagesResponse(
      numPagesHydrated=0,
      error=str(fetchAllTopicsRes.error)
    )

  # Hydrate all the corresponding topic pages for those topics
  topicList = set([t.TopicName for t in fetchAllTopicsRes.topics])
  logger.info("Total number of topics: " + str(len(topicList)))

  if not hydrateTopicPagesRequest.force_update:
    # If not force upgrade, then get only the topics that don't already have a topic page
    topicsToHydrateList = []
    for topic in topicList:
      fetchTopicPageRes = fetchTopicPageByTopic(
        FetchTopicPageRequest(
          topic=topic,
        )
      )
      # If the topic page doesn't exist, then create a new one
      if fetchTopicPageRes.topic_page is None:
        logger.info("Topic page for topic " + str(topic) + " already exists")
        topicsToHydrateList.append(topic)

  else:
    topicsToHydrateList = topicList

  logger.info("Number of topic pages to hydrate: " + str(len(topicsToHydrateList)))

  # Aysynchronously populate all of the topic pages to display on the home page
  pool = ThreadPool(processes=1)
  getTopicPageRequests = [GetTopicPageRequest(topicName = topic, savePage=True)  for topic in topicsToHydrateList]
  topicPages = pool.map(getTopicPage, getTopicPageRequests)

  i = 0
  for topicPage in topicPages:
    logger.info("Topic page " + str(i))
    logger.info(topicPage)
    i+= 1

  pool.close()
  pool.join()

  return HydrateTopicPagesResponse(
    numPagesHydrated=len(topicsToHydrateList),
    error=None
  )


def fetchTopicPagesBatch(fetchTopicPageBatchRequest):
  """
    This endpoint handles pagination for topic pages including a limit and offset and directly querying by the time the topic page was created.
  """

  fetchTopicPageBatchRes = fetchTopicPageBatch(fetchTopicPageBatchRequest)

  if fetchTopicPageBatchRes.error != None:
    return FetchTopicPageBatchResponse(
      topicPages=None,
      error=fetchTopicPageBatchRes.error
    )

  return fetchTopicPageBatchRes



