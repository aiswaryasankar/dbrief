from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from newspaper import Article
import feedparser
from .models import ArticleModel
import schedule
import time
# from logtail import LogtailHandler
import logging
import datetime
from topicModeling.training import Top2Vec
from constants import rss_feeds
import controller
import repository
import topicModeling.handler as tpHandler
import idl

# handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# logger.addHandler(handler)
# logger.info('LOGTAIL TEST')

@api_view(['GET', 'POST'])
def hello_world(request):
  if request.method == 'POST':
    return Response({"Message": "Got data", "data": request.data})

  return Response({"message": "Hello world lol"})


@api_view(['GET'])
def populate_articles():
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

  articleText = []
  urlList = controller.process_rss_feed()

  for url in urlList:

    # Hydrate article
    article = controller.hydrate_article(url)

    # Save to database and fetch article id
    articleId = repository.saveArticle(
      idl.SaveArticleRequest(
        url=url,
        text=article.text,
        title=article.title,
        date=article.publish_date,
        imageURL=article.top_image,
      )
    )

    # Add document to topic model with text and doc id
    addedToTopicModel = tpHandler.add_document(
      idl.AddDocumentRequest(
        documents=[article.text],
        doc_ids=[articleId],
      )
    )

    # Get topic for the document from the topic model
    getTopicResponse = tpHandler.get_document_topic(
      idl.GetDocumentTopicRequest(
        doc_ids=[articleId],
        reduced=False,
        num_topics=1,
      )
    )

    # Get the subtopic for the document from the topic model
    getSubtopicResponse = tpHandler.get_document_topic(
      idl.GetDocumentTopicRequest(
        doc_ids=[articleId],
        reduced=False,
        num_topics=1,
      )
    )

    # Get the polarity of the document from the topic model

    # Get the fact from the document

    # Update the db with additional data


    articleText.append(article.text)

  return Response({"article text": articleText})






