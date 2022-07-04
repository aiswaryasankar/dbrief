from articleRec.repository import fetchArticlesByUrl
from .models import TopicPageModel
import logging
from idl import *
from topicFeed import handler as tfHandler
from logtail import LogtailHandler
from datetime import datetime

"""
  This file will include all the basic database CRUD operations including:
    - Save
    - Query
    - Delete
    - Update
"""

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)


def saveTopicPage(saveTopicPageRequest):
  """
    Will save the topic page in the database
  """

  # Check the timestamp of the entry and overwrite if the timestamp is > 24 hrs old
  try:
    topicPageEntry, created = TopicPageModel.objects.update_or_create(
      topic = saveTopicPageRequest.topic,
      defaults={
        "topic" : saveTopicPageRequest.topic,
        "topicId" :  saveTopicPageRequest.topicId,
        "summary" : saveTopicPageRequest.summary,
        "title" : saveTopicPageRequest.title,
        "imageURL" : saveTopicPageRequest.imageURL,
        "urls" : saveTopicPageRequest.urls,
        "topArticleId" : saveTopicPageRequest.topArticleId,
        "isTimeline" : saveTopicPageRequest.isTimeline,
        "createdAt": datetime.now(),
      },
    )
    if created:
      logger.info("Saved topic page entry to the database: " + str(saveTopicPageRequest.topic))

  except Exception as e:
    logger.info("Failed to save topic page for topic " + str(saveTopicPageRequest.topic) + " to the database: " + str(e))
    return SaveTopicPageResponse(
      topicPageId=None,
      error=str(e)
    )

  logger.info("Saved topic page for topic " + str(saveTopicPageRequest.topic) + " entry to the database: " + str(topicPageEntry.topicPageId))
  return SaveTopicPageResponse(
    topicPageId=topicPageEntry.topicPageId,
    error=None
  )

def fetchTopicPageBatch(fetchTopicPageBatchRequest):
  """
    Fetch topic pages in batch
  """
  pass


def fetchTopicPage(fetchTopicPageRequest):
  """
    Fetch the topic page using the topic
  """

  try:
    topicPageRes = TopicPageModel.objects.get(topic=fetchTopicPageRequest.topic)

    topicPage = TopicPage(
      Title = topicPageRes.title,
      ImageURL = topicPageRes.imageURL,
      MDSSummary = topicPageRes.summary,
      Facts = [],
      Opinions = [],
      TopArticleID = topicPageRes.topArticleId,
      TopicID= topicPageRes.topicId,
      TopicName=topicPageRes.topic,
      IsTimeline=topicPageRes.isTimeline,
      CreatedAt=topicPageRes.createdAt,
    )

    # Hydrate the appropriate facts and opinions by querying articles from the articleRec table
    facts = []
    opinions = []
    urls = topicPageRes.urls.split(",")
    urls = [url.strip() for url in urls]
    fetchArticlesByUrlRes = fetchArticlesByUrl(urls)

    if fetchArticlesByUrlRes.error != None:
      logger.warn("Failed to hydrate facts and opinion in the topic page")
      return FetchTopicPageResponse(
        topic_page=None,
        error=fetchArticlesByUrlRes.error,
      )

    for article in fetchArticlesByUrlRes.articleList:
      source = tfHandler.parseSource(article.url)

      if article.topFact != None and len(article.topFact) > 100:
        facts.append(Fact(
          Quote(
            Text=article.topFact,
            Author=article.authors,
            SourceName=source,
            SourceURL=article.url,
            ImageURL=article.imageURL,
            Polarization=article.polarizationScore,
            Timestamp=article.date,
            ArticleID=article.id,
          )
        ))

      if article.topPassage != None and len(article.topPassage) > 100:
        opinions.append(Opinion(
          Quote(
            Text=article.topPassage,
            Author=article.authors,
            SourceName=source,
            SourceURL=article.url,
            ImageURL=article.imageURL,
            Polarization=article.polarizationScore,
            Timestamp=article.date,
            ArticleID=article.id,
          )
        ))

    topicPage.Facts = facts
    topicPage.Opinions = opinions

    return FetchTopicPageResponse(
      topic_page=topicPage,
      error=None,
    )

  except Exception as e:
    logger.warn("Failed to fetch topic page for topic: " + str(fetchTopicPageRequest.topic) + " " + str(e))

    return FetchTopicPageResponse(
      topic_page=None,
      error=str(e),
    )


