from rest_framework.decorators import api_view
from rest_framework.response import Response
from newspaper import Article
import feedparser
from .models import ArticleModel
import schedule
import time
from logtail import LogtailHandler
import logging
import datetime
from topicModeling.training import Top2Vec


rss_feeds = [
  "https://rsshub.app/apnews/topics/apf-topnews",
  "https://www.economist.com/the-world-this-week/rss.xml",
  "https://www.economist.com/special-report/rss.xml",
  "https://www.economist.com/europe/rss.xml",
  "https://www.economist.com/united-states/rss.xml",
  "https://www.economist.com/asia/rss.xml",
  "https://www.economist.com/middle-east-and-africa/rss.xml",
  "https://www.economist.com/china/rss.xml",
  "https://www.economist.com/international/rss.xml",
  "https://www.economist.com/business/rss.xml",
  "https://www.economist.com/finance-and-economics/rss.xml",
  "https://www.economist.com/science-and-technology/rss.xml",
  "https://feeds.npr.org/1001/rss.xml",
  "https://rss.nytimes.com/services/xml/rss/nyt/US.xml",
	"https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
	"https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
	"https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml",
	"https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
	"https://rss.nytimes.com/services/xml/rss/nyt/US.xml",
	"https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
	"http://feeds.washingtonpost.com/rss/politics",
	"http://feeds.washingtonpost.com/rss/opinion",
	"http://feeds.washingtonpost.com/rss/world",
	"http://feeds.washingtonpost.com/rss/business",
	"https://www.foxnews.com/about/rss/politics",
	"http://rss.cnn.com/rss/cnn_world.rss",
	"http://rss.cnn.com/rss/cnn_us.rss",
	"http://rss.cnn.com/rss/cnn_allpolitics.rss",
	"http://rss.cnn.com/rss/cnn_tech.rss",
	"https://www.nationalreview.com/corner/feed/",
	"https://feeds.a.dj.com/rss/RSSOpinion.xml",
	"https://feeds.a.dj.com/rss/RSSWorldNews.xml",
	"https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml",
	"https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
	"https://feeds.a.dj.com/rss/RSSWSJD.xml",
	"http://feeds.bbci.co.uk/news/business/rss.xml",
	"http://feeds.bbci.co.uk/news/politics/rss.xml",
	"http://feeds.bbci.co.uk/news/world/rss.xml",
	"http://feeds.bbci.co.uk/news/technology/rss.xml",
	"http://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
  "http://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml?edition=int",
	"https://rss.politico.com/economy.xml",
	"https://rss.politico.com/politics-news.xml",
	"https://rss.politico.com/congress.xml",
	"https://rss.politico.com/healthcare.xml",
	"https://rss.politico.com/defense.xml",
	"https://rss.politico.com/energy.xml",
	"https://fivethirtyeight.com/all/feed",
	"https://www.vox.com/rss/index.xml",
	"https://www.washingtontimes.com/rss/headlines/opinion/advocacy/",
	"https://www.washingtontimes.com/rss/headlines/opinion/political-theater/",
	"https://www.washingtontimes.com/rss/headlines/news/analysis/",
	"https://www.washingtontimes.com/rss/headlines/news/business-economy/",
	"https://www.washingtontimes.com/rss/headlines/news/inside-politics/",
	"https://www.washingtontimes.com/rss/headlines/news/inside-china/",
	"https://www.washingtontimes.com/rss/headlines/news/politics/",
  "https://thehill.com/taxonomy/term/1116/feed",
  "https://thehill.com/rss/syndicator/19110",
  "https://thehill.com/rss/syndicator/19109",
  "https://thehill.com/taxonomy/term/43/feed",
  "https://thehill.com/taxonomy/term/27/feed",
  "https://thehill.com/taxonomy/term/38/feed",
  "https://thehill.com/taxonomy/term/33/feed",
  "https://thehill.com/taxonomy/term/30/feed",
  "https://thehill.com/taxonomy/term/28/feed",
  "https://thehill.com/taxonomy/term/39/feed",
  "https://thehill.com/taxonomy/term/49/feed",
  "https://thehill.com/taxonomy/term/20/feed",
]


### Endpoints

@api_view(['GET', 'POST'])
def hello_world(request):
  if request.method == 'POST':
    return Response({"Message": "Got data", "data": request.data})

  return Response({"message": "Hello world lol"})


@api_view(['GET'])
def fetch_and_hydrate_articles(request):

  handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
  logger = logging.getLogger(__name__)
  logger.handlers = []
  logger.addHandler(handler)
  logger.info('LOGTAIL TEST')

  urls = []
  articleText = []
  for entry in rss_feeds:

    feed = feedparser.parse(entry)

    for article in feed.entries:
      try:
        urls.append(article.links[0].href)
      except Exception as e:
        continue

  for url in urls:
    logger.info('URL')
    logger.info(url)
    article = Article(url)
    article.download()
    try:
      article.parse()
    except Exception as e:
      continue

    title = article.title
    text = article.text
    author = article.authors
    publish_date = article.publish_date

    articleEntry = ArticleModel(
      url = url,
      title = title,
      text = text,
      author = author,
      publish_date = publish_date,
    )
    try:
      articleEntry.save()
      print("Article saved to the database: ", articleEntry)
      logger.info("Saved article to the database: ", articleEntry)
    except Exception as e:
      logger.warn("Failed to save article to the database: ", articleEntry)
      continue

    articleText.append(article.text)

  return Response({"article text": articleText})


### Helper Functions

def cron_job_test(request):

  print("Started the cron job")
  handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
  logger = logging.getLogger(__name__)
  logger.handlers = []
  logger.addHandler(handler)
  logger.info('LOGTAIL TEST')


@api_view(['GET'])
def retrain_topic_model(request):
  """
    This endpoint will first fetch all the documents from the database and keep it in memory
    It will then pass in the doc_ids and the document text to the topic model endpoint
    The topic model endpoint will then store the weights in a file that it will read during evaluation
  """

  documents = ArticleModel.objects.all()
  data = [doc.text for doc in documents]
  doc_ids = [doc.articleId for doc in documents]

  startTime = datetime.datetime.now()
  model = Top2Vec(documents=data, speed="learn",embedding_model='sentence-transformers', workers=4, document_ids=doc_ids)
  endTime = datetime.datetime.now()

  docIndex = Top2Vec.index_document_vectors(model)
  wordIndex = Top2Vec.index_word_vectors(model)
  savedModel = Top2Vec.save(self = model, file='./modelWeights/topicModelWeights')
  loadedModel = Top2Vec.load("./modelWeights/topicModelWeights")

  print(endTime - startTime)
  return Response()


@api_view(['GET'])
def query_documents_url(request):
  """
    Gets the similar documents to a given document
  """
  top2vecModel = Top2Vec.load("./modelWeights/topicModelWeights")
  article = Article("https://www.nytimes.com/2021/11/27/opinion/republicans-trump.html")
  article.download()
  try:
    article.parse()
  except Exception as e:
    print("Failed to hydrate the article request")

  text = article.text

  similarDocs = Top2Vec.query_documents(self=top2vecModel, query=text, num_docs=10, return_documents=True, use_index=True, ef=200)
  print("Documents returned")
  print(similarDocs)

  return Response({"similar docs": similarDocs[0]})

def index_document_vectors(request):
  """
    This endpoint is responsible for re-indexing the documents after the topic model has been regenerated. In the case of individual articles being added to the topic model, it will be handled through add_document.
  """
  pass

schedule.every().day.at("10:00").do(fetch_and_hydrate_articles)



