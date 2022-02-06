import logging
from articleRec import handler as articleRecHandler
from topicModeling import handler as topicModelingHandler
from mdsModel.handler import *
from datetime import datetime
import idl
from userPreferences import handler as upHandler
from topicFeed import handler as topicFeedHandler
import asyncio

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)


def hydrateHomePage(hydrateHomePageRequest):
  """
    The home page will consist of all the topic modals.  It will first query for the top topics, then for each topic it will include the MDS, and a list of the facts for that topic and a top image.  If the user is signed in then it will first query for the topics that the user has saved and surface those first.  After that it will surface the rest of the top topics.
  """

  topicList = []

  # If the user is following any topics, get those topics first
  if hydrateHomePageRequest.user_id != None:
    getTopicsYouFollowResponse = upHandler.get_topics_you_follow(
      GetTopicsForUserRequest(
        user_id = hydrateHomePageRequest.user_id
      )
    )
    if getTopicsYouFollowResponse.error != None:
      return HydrateHomePageResponse(
        topicPages= [],
        error=str(getTopicsYouFollowResponse.error)
      )
    topicList = [t.topic for t in getTopicsYouFollowResponse.topics]

  # If the user isn't following any topics get the topic topics currently
  else:
    getTopicsResponse = topicFeedHandler.get_topics(
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
    topicList = getTopicsResponse.topic_words

  # # Aysynchronously populate all of the topic pages to display on the home page
  # coroutines = [topicFeedHandler.getTopicPage(topicName=topic) for topic in topicList]
  # getTopicPageRes = await asyncio.gather(*coroutines)
  # print(getTopicPageRes)


