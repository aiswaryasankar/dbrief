import logging
import threading
from articleRec import handler as articleRecHandler
from topicModeling import handler as topicModelingHandler
from mdsModel.handler import *
from datetime import datetime
from idl import *
from userPreferences import handler as upHandler
from topicFeed import handler as topicFeedHandler
from topicModeling import handler as topicModelingHandler
from multiprocessing.pool import ThreadPool, Pool


handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)


def hydrateHomePageCached(hydrateHomePageRequest):
  """
    This sets up a flow that directly reads the topic pages from the cached pages stored in the database.
  """
  # It needs to search topic pages by the topic name
  topicList = []

  beforeGetTopicsYouFollow = datetime.now()
  # If the user is following any topics, get those topics first
  if hydrateHomePageRequest.userId != None:
    getTopicsYouFollowResponse = upHandler.get_topics_you_follow(
      GetTopicsForUserRequest(
        user_id = hydrateHomePageRequest.userId
      )
    )
    if getTopicsYouFollowResponse.error != None:
      logger.warn("error in getTopicsYouFollow")
      return HydrateHomePageResponse(
        topicPages= [],
        error=str(getTopicsYouFollowResponse.error)
      )
    topicList = [t.TopicName for t in getTopicsYouFollowResponse.topics]
    logger.info(topicList)

  afterGetTopicsYouFollow = datetime.now()
  logger.info("Time taken to getTopicsYouFollow: %s", str(afterGetTopicsYouFollow-beforeGetTopicsYouFollow))

  # If the user isn't following any topics get the top topics currently
  beforeGetTopics = datetime.now()
  if len(topicList) < 5:
    getTopicsResponse = topicModelingHandler.get_topics(
      GetTopicsRequest(
        num_topics=30,
        reduced = False,
      )
    )
    if getTopicsResponse.error != None:
      return HydrateHomePageResponse(
        topicPages =[],
        error=str(getTopicsResponse.error)
      )
    topicList.extend(getTopicsResponse.topic_words)

  logger.info("The topic list is: " + str(topicList))
  logger.info(topicList)
  afterGetTopics = datetime.now()
  logger.info("Time to getTopics: %s", str(afterGetTopics-beforeGetTopics))


  topicPages = []
  for topic in topicList:
    fetchTopicPageByTopicRes = topicFeedHandler.fetchTopicPageByTopic(
      fetchTopicPageByTopicRequest=FetchTopicPageRequest(
        topic=topic,
      )
    )
    logger.info("Fetch topic page cached: ")
    logger.info(fetchTopicPageByTopicRes)
    if fetchTopicPageByTopicRes.error == None and fetchTopicPageByTopicRes.topic_page !=  None:
      topicPages.append(fetchTopicPageByTopicRes)
    else:
      logger.warn("Failed to hydrate topic page: " + str(fetchTopicPageByTopicRes.error))

  # Order the topic pages by date and possibly include a date header in between the pages
  sortedTopicPages = sorted(topicPages, key=lambda fetchTopicPageRes: fetchTopicPageRes.topic_page.CreatedAt, reverse=True)

  logger.info("number of topic pages: " + str(len(sortedTopicPages)))
  return HydrateHomePageResponse(
    topicPages=sortedTopicPages,
    error = None
  )


def hydrateHomePage(hydrateHomePageRequest):
  """
    The home page will consist of all the topic modals.  It will first query for the top topics, then for each topic it will include the MDS, and a list of the facts for that topic and a top image.  If the user is signed in then it will first query for the topics that the user has saved and surface those first.  After that it will surface the rest of the top topics.
  """

  topicList = []

  beforeGetTopicsYouFollow = datetime.now()
  # If the user is following any topics, get those topics first
  if hydrateHomePageRequest.userId != None:
    getTopicsYouFollowResponse = upHandler.get_topics_you_follow(
      GetTopicsForUserRequest(
        user_id = hydrateHomePageRequest.userId
      )
    )
    if getTopicsYouFollowResponse.error != None:
      logger.warn("error in getTopicsYouFollow")
      return HydrateHomePageResponse(
        topicPages= [],
        error=str(getTopicsYouFollowResponse.error)
      )
    topicList = [t.TopicName for t in getTopicsYouFollowResponse.topics]
    logger.info(topicList)

  afterGetTopicsYouFollow = datetime.now()
  logger.info("Time taken to getTopicsYouFollow: %s", str(afterGetTopicsYouFollow-beforeGetTopicsYouFollow))

  # If the user isn't following any topics get the top topics currently
  beforeGetTopics = datetime.now()
  if len(topicList) < 5:
    getTopicsResponse = topicModelingHandler.get_topics(
      GetTopicsRequest(
        num_topics=5,
        reduced = False,
      )
    )
    if getTopicsResponse.error != None:
      return HydrateHomePageResponse(
        topicPages =[],
        error=str(getTopicsResponse.error)
      )
    topicList.extend(getTopicsResponse.topic_words)

  logger.info("The topic list is")
  logger.info(topicList)
  afterGetTopics = datetime.now()
  logger.info("Time to getTopics: %s", str(afterGetTopics-beforeGetTopics))

  beforeParallelHydration = datetime.now()
  # Aysynchronously populate all of the topic pages to display on the home page
  pool = ThreadPool(processes=len(topicList))
  getTopicPageRequests = [GetTopicPageRequest(topicName = topic)  for topic in topicList]
  topicPages = pool.map(topicFeedHandler.getTopicPage, getTopicPageRequests)

  i = 0
  for topicPage in topicPages:
    logger.info("Topic page " + str(i))
    logger.info(topicPage)
    i+= 1

  pool.close()
  pool.join()

  afterParallelHydration = datetime.now()
  logger.info("Time to parallel hydrate: %s", str(afterParallelHydration-beforeParallelHydration))

  return HydrateHomePageResponse(
    topicPages=topicPages,
    error = None
  )

