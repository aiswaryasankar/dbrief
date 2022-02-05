"""
  This service is primarily responsible for serving all the content for the topic pages. This service will handle the remaining calls to generate the topic model.  This includes GetTopicPageByURL, GetTopicPageByArticleId, GetTopicPageBySearchString, GetTopicPageByTopicId.  It will also surface the side bars for WhatsHappening, GetRecommendedTopicsForUser and GetTopicsYouFollow.  The 4 methods that handle populating the page will essentially take care of mapping the search query to the appropriate form and then fetching all the content necessary for the topic page. Each will call the same base function to hydrate the information.
"""

import logging
from articleRec import handler as articleRecHandler
from topicModeling import handler as tpHandler
from mdsModel.handler import *
from datetime import datetime
import idl

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)


def getTopicPageHydrated(text):
  """
    This helper function will take in article text and return the GetTopicPageResponse
  """
  pass


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

  if getTopicPageRequest.url != "":
    # Try to fetch the article if already in db
    articleId = -1
    fetchArticlesResponse = articleRecHandler.fetchArticles(
      FetchArticlesRequest(
        articleUrls=[getTopicPageRequest.url]
      )
    )

    if fetchArticlesResponse.error != None or len(fetchArticlesResponse.articleList) == 0:
      # Hydrate the article if not in db and rewrite
      hydrateArticleResponse = articleRecHandler.hydrate_article(
        HydrateArticleRequest(
          url=getTopicPageRequest.url
        )
      )
      if hydrateArticleResponse.error != None:
        return GetTopicPageResponse(
          topic_page=None,
          error=str(hydrateArticleResponse.error),
        )

      print("Populating the article")
      # Populate the article
      populateArticleRes = articleRecHandler.populate_article_by_url(
        PopulateArticleRequest(
          url = getTopicPageRequest.url,
        )
      )
      if populateArticleRes.error != None:
        logger.warn("Failed to populate article in the db")
        return GetTopicPageResponse(
          topic_page=None,
          error=str(populateArticleRes.error),
        )
      else:
        article = hydrateArticleResponse.article
        articleId = populateArticleRes.id
        text = hydrateArticleResponse.article.text

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

    logger.info("Topics fetched")
    logger.info(fetchTopicInfoBatchResponse.topics)
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

  logger.info("query doc response")
  logger.info(queryDocumentsResponse)
  # Fetch the related articles from the database
  fetchArticlesResponse = articleRecHandler.fetchArticles(
    FetchArticlesRequest(
      articleIds= queryDocumentsResponse.doc_ids,
    )
  )
  if fetchArticlesResponse.error != None:
    return GetTopicPageResponse(topic_page=None, error=str(fetchArticlesResponse.error))

  # TODO: GetTitleSummaryForSearch in order to fetch the title for the articles

  # GetMDS to get the MDS for the articles
  articles = ""
  topImageUrl = ""
  for a in fetchArticlesResponse.articleList:
    articles += a.text
    if a.imageURL != "":
      topImageUrl = a.imageURL

  getMDSSummaryResponse = get_mds_summary_handler(
    GetMDSSummaryRequest(
      articles=articles
    )
  )
  if getMDSSummaryResponse.error != None:
    return GetTopicPageResponse(topic_page=None, error=str(getMDSSummaryResponse.error))

  logger.info("MDS SUMMARY")
  logger.info(getMDSSummaryResponse.summary)
  facts = []
  passages = []

  for article in fetchArticlesResponse.articleList:
    if article.authors is not None and article.authors != "[]":
      author = article.authors.split(",")[0].replace("[", "").replace('\'', "").replace("]", "")
    else:
      author = parseSource(article.url)

    if article.date == "":
      article.date = datetime.now()

    source = parseSource(article.url)
    logger.info("URL %s and source %s", article.url, source)
    if article.topFact != None:
      facts.append(
        Fact(
          Quote= Quote(
            Text=article.topFact,
            SourceName=source,
            Author=author,
            SourceURL=article.url,
            ArticleID=article.id,
            Polarization=0,
            Timestamp=article.date,
            ImageURL=article.imageURL,
          )
        )
      )

    if article.topPassage != None:
      passages.append(
        Opinion(
          Quote= Quote(
            Text=article.topPassage,
            SourceName=source,
            Author=author,
            SourceURL=article.url,
            ArticleID=article.id,
            Polarization=article.polarizationScore,
            Timestamp=article.date,
            ImageURL=article.imageURL,
          )
        )
      )

  isTimeline = True
  if len(passages) > 6:
    isTimeline = False

  topic_page = TopicPage(
    Title = article.title,
    MDSSummary = getMDSSummaryResponse.summary,
    Facts = facts,
    Opinions = passages,
    TopArticleID = int(articleId),
    IsTimeline = isTimeline,
    TopicID = None,
    ImageURL = topImageUrl,
  )
  logger.info("TOPIC PAGE")
  logger.info(topic_page)

  return GetTopicPageResponse(
    topic_page=topic_page,
    error= None,
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
        num_docs=2,
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

  articleInfo = []
  for article in fetchArticlesByIdResponse.articleList:
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


def parseSource(url):
  """
    Massive switch condition to tie the url with the source
  """
  source = ""
  if "techcrunch" in url:
    source = "Tech Crunch"
  if "technologyreview" in url:
    source = "Technology Review"
  if "arstechnica" in url:
    source = "Ars Technica"
  if "venturebeat" in url:
    source = "Venture Beat"
  if "vox" in url:
    source = "Vox"
  if "wired" in url:
    source = "Wired"
  if "theverge" in url:
    source = "The Verge"
  if "Ieee" in url:
    source = "IEEE"
  if "cnet" in url:
    source = "CNet"
  if "businessinsider" in url:
    source = "BusinessInsider"
  if "TechSpot" in url:
    source = "Tech Spot"
  if "hackernoon" in url:
    source = "Hacker Noon"
  if "appleinsider" in url:
    source = "Apple Insider"
  if "latimes" in url:
    source = "LA Times"
  if "cnn" in url:
    source = "CNN"
  if "huffpost" in url:
    source = "Huffington Post"
  if "usatoday" in url:
    source = "USA Today"
  if "foxnews" in url:
    source = "Fox News"
  if "breitbart" in url:
    source = "Breitbart"
  if "washingtontimes" in url:
    source = "Washington Times"
  if "thehill" in url:
    source = "The Hill"
  if "apnews" in url:
    source = "AP News"
  if "npr" in url:
    source = "NPR"
  if "nytimes" in url:
    source = "NY Times"
  if "washingtonpost" in url:
    source = "Washington Post"
  if "apnews" in url:
    source = "AP News"
  if "nationalreview" in url:
    source = "National Review"
  if "dj" in url:
    source = "Al Jazeera"
  if "bbc" in url:
    source = "BBC"
  if "politico" in url:
    source = "Politico"
  if "economist" in url:
    source = "Economist"

  return source


