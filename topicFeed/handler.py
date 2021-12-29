"""
  This service is primarily responsible for serving all the content for the topic pages. This service will handle the remaining calls to generate the topic model.  This includes GetTopicPageByURL, GetTopicPageByArticleId, GetTopicPageBySearchString, GetTopicPageByTopicId.  It will also surface the side bars for WhatsHappening, GetRecommendedTopicsForUser and GetTopicsYouFollow.  The 4 methods that handle populating the page will essentially take care of mapping the search query to the appropriate form and then fetching all the content necessary for the topic page. Each will call the same base function to hydrate the information.
"""

import logging
from articleRec.handler import *
from topicModeling.handler import *
from mdsModel.handler import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
import datetime
import idl

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)



def getTopicPage(getTopicPageByURLRequest):
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

  # Try to fetch the article if already in db
  articleId = -1
  fetchArticlesResponse = fetchArticlesByUrl([getTopicPageByURLRequest.source])

  if fetchArticlesResponse.error != None or len(fetchArticlesResponse.articleList) == 0:
    # Hydrate the article if not in db and rewrite
    article = hydrate_article(getTopicPageByURLRequest.source)

    # Populate the article
    populateArticleRes = populate_article_by_url(
      PopulateArticleRequest(
        url = getTopicPageByURLRequest.source,
      )
    )
    if populateArticleRes.error != None:
      logger.warn("Failed to populate article in the db")
    else:
      articleId = populateArticleRes.id

  else:
    article = fetchArticlesResponse.articleList[0]
    articleId = fetchArticlesResponse.articleList[0].id

  # Query for top documents based on the article text
  queryDocumentsResponse = query_documents_url(
    QueryDocumentsRequest(
      query=article.text,
      num_docs=10,
      return_docs=False,
      use_index=True,
      ef=200,
    )
  )
  if queryDocumentsResponse.error != None:
    return GetTopicPageResponse(topic_page=None, error=str(queryDocumentsResponse.error))

  # Fetch the related articles from the database
  fetchArticlesResponse = fetchArticlesById(
    FetchArticlesRequest(
      articleIds= queryDocumentsResponse.doc_ids,
    )
  )
  if fetchArticlesResponse.error != None:
    return GetTopicPageResponse(topic_page=None, error=str(fetchArticlesResponse.error))

  # TODO: GetTitleSummaryForSearch in order to fetch the title for the articles

  # GetMDS to get the MDS for the articles
  articles = ""
  for a in fetchArticlesResponse.articleList:
    articles += a.text

  getMDSSummaryResponse = get_mds_summary_handler(
    GetMDSSummaryRequest(
      articles=articles
    )
  )
  if getMDSSummaryResponse.error != None:
    return GetTopicPageResponse(topic_page=None, error=str(getMDSSummaryResponse.error))

  # Aggregate the list of facts for the page
  facts = []
  passages = []

  for article in fetchArticlesResponse.articleList:
    if article.topFact != None:
      facts.append(
        Fact(
          Quote= Quote(
            Text=article.topFact,
            SourceName="source",
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
            SourceName="source",
            SourceURL=article.url,
            ArticleID=article.id,
            Polarization=article.polarizationScore,
            Timestamp=article.date,
            ImageURL=article.imageURL,
          )
        )
      )

  topic_page = TopicPage(
    Title = article.title,
    MDSSummary = getMDSSummaryResponse.summary,
    Facts = facts,
    Opinions = passages,
    TopArticleID = articleId,
    TopicID = None,
    Timeline = None,
  )
  return GetTopicPageResponse(
    topic_page=topic_page,
    error= None,
  )


def whatsHappening(request):
  pass



def getRecommendedTopicsForUser(request):
  pass



def getTopicsYouFollow(request):
  pass



