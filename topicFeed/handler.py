"""
  This service is primarily responsible for serving all the content for the topic pages. This service will handle the remaining calls to generate the topic model.  This includes GetTopicPageByURL, GetTopicPageByArticleId, GetTopicPageBySearchString, GetTopicPageByTopicId.  It will also surface the side bars for WhatsHappening, GetRecommendedTopicsForUser and GetTopicsYouFollow.  The 4 methods that handle populating the page will essentially take care of mapping the search query to the appropriate form and then fetching all the content necessary for the topic page. Each will call the same base function to hydrate the information.
"""

import logging
from articleRec.handler import *
from topicModeling.handler import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
import datetime
import idl

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)



def getTopicPage(request):
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

  topArticleUrl = ""

  if request.url != "":
    # Use the provided url to create the topic page
    topArticleUrl = request.url

  if request.articleId != "":
    # Use the articleId to fetch the article from the db
    article = fetchArticlesById(idl.FetchArticlesRequest(
      articleIds=[request.articleId]
    ))
    if len(article.articleList[0]) == 0:
      return GetTopicPageResponse(
        topic_page= None,
        error= ValueError("Failed to fetch article for provided articleId")
      )
    topArticleUrl = article.articleList[0].url

  if request.topicString != "":
    pass
    # Fetch the topicId given the topic string


    # Fetch the top document that corresponds to that topicId


  if request.searchString != "":
    pass

  article = hydrate_article(topArticleUrl)

  # Query for top documents based on the article text
  queryDocumentsResponse = query_documents_url(QueryDocumentsRequest(
    query=article.text,
    num_docs=10,
    return_docs=False,
    use_index=True,
    ef=200,
  ))

  # Fetch the related articles from the database
  articles = fetchArticlesById(FetchArticlesRequest(
    articleIds= queryDocumentsResponse.doc_ids,
  ))

  # GetTitleSummaryForSearch in order to fetch the title for the articles


  # GetMDS to get the MDS for the articles


  # Optionally query for the key facts and passages if not stored in the DB already




def whatsHappening(request):
  pass



def getRecommendedTopicsForUser(request):
  pass



def getTopicsYouFollow(request):
  pass



