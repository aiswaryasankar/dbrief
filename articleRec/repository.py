from .models import ArticleModel
import logging
from idl import *
from logtail import LogtailHandler

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


def saveArticle(saveArticleRequest):
  """
    Will save the article to the database.  If the article already exists it will update the existing article instead.
  """

  a = saveArticleRequest.article
  url = a.url
  title = a.title
  text = a.text
  author = a.authors
  publish_date = a.date
  topic = a.topic
  parentTopic = a.parentTopic
  topPassage = a.topPassage
  topFact = a.topFact
  image= a.imageURL
  polarizationScore = a.polarizationScore
  created = False

  try:
    articleEntry, created = ArticleModel.objects.update_or_create(
      url = url,
      defaults={
        'title': title,
        'text': text,
        'author': author,
        'publish_date': publish_date,
        'topic': topic,
        'parent_topic': parentTopic,
        'top_passage': topPassage,
        'top_fact': topFact,
        'polarization_score': polarizationScore,
        'image': image,
      },
    )
    if created:
      logger.info('saved article', extra={
          "item": {
              "url": url,
              "res": articleEntry,
              "id" : articleEntry.articleId,
              "created": created,
          }
      })
      logger.info("Saved article to the database: ")
    else:
      logger.info("Updated already existing article")

  except Exception as e:
    logger.warn("Failed to save article to the database")
    logger.warn(e)

    return SaveArticleResponse(id=None, error=e, created=created)

  return SaveArticleResponse(id=articleEntry.articleId, error=None, created=created)


def fetchArticles(fetchArticlesRequest):
  """
    Will handle fetching articles based on any filter parameters that are specified.
  """
  field = ""
  filterList = []
  articleList = []

  if fetchArticlesRequest.articleIds != []:
    field = "articleId"
    filterList = fetchArticlesRequest.articleIds
  elif fetchArticlesRequest.articleUrls != []:
    field = "url"
    filterList = fetchArticlesRequest.articleUrls

  for elem in filterList:
    try:
      if field=="articleId":
        article = ArticleModel.objects.get(articleId=elem)
      elif field=="url":
        article = ArticleModel.objects.get(url=elem)

      a = Article(
          id=article.articleId,
          url=article.url,
          authors=article.author,
          text=article.text,
          title=article.title,
        )

      if article.topic:
        a.topic = article.topic
      if article.parent_topic:
        a.parentTopic = article.parent_topic
      if article.publish_date:
        a.topic = article.publish_date
      if article.image:
        a.imageURL = article.image
      if article.polarization_score:
        a.polarizationScore = article.polarization_score
      if article.top_passage:
        a.topPassage = article.top_passage
      if article.top_fact:
        a.topFact = article.top_fact

      articleList.append(a)

    except Exception as e:
      logger.warn("Failed to fetch article from database with attribute %s", elem)
      print(e)
      return FetchArticlesResponse(
        articleList=articleList,
        error=e,
      )

  return FetchArticlesResponse(
    articleList=articleList,
    error=None,
  )


def fetchAllArticles():
  """
    Will fetch the entire list of articles from the database and return them as hydrated Article objects
  """

  articleList = []
  articleText = []

  for article in ArticleModel.objects.all():
    try:
      a = Article(
          id=article.articleId,
          url=article.url,
          authors=article.author,
          text=article.text,
          title=article.title,
        )

      if article.topic:
        a.topic = article.topic
      if article.parent_topic:
        a.parentTopic = article.parent_topic
      if article.publish_date:
        a.topic = article.publish_date
      if article.image:
        a.imageURL = article.image
      if article.polarization_score:
        a.polarizationScore = article.polarization_score
      if article.top_passage:
        a.topPassage = article.top_passage
      if article.top_fact:
        a.topFact = article.top_fact

      articleList.append(a)
      articleText.append(article.text.replace("\n", ""))
    except Exception as e:
      logger.warn("Failed to fetch article from database", extra={
        "article": article,
        "error": e,
      })
      print(e)

  f = open("articles.txt", "w")

  for elem in articleText:
    f.write(elem+"\n")
  f.close()

  return FetchArticlesResponse(
    articleList=articleList,
    error=None,
  )


def fetchArticlesById(fetchArticlesRequest):
  """
    Will fetch articles by the article Id and populate the Article entity
  """
  hydratedArticles = []
  articleIds = fetchArticlesRequest.articleIds

  for id in articleIds:
    try:
      article = ArticleModel.objects.get(articleId=id)
      fetchRes = articleResToModel(article)

      if fetchRes.error != None:
        logger.warn("Failed to fetch article with id")
        logger.warn(fetchRes.error)
        continue
      else:
        hydratedArticles.extend(fetchRes.articleList)
    except:
      logger.warn("Failed to fetch article with id")

  return FetchArticlesResponse(
    articleList=hydratedArticles,
    error=None,
  )


def articleResToModel(article):
  """
    Will map a db article to the Article IDL to return
  """
  try:
    a = Article(
      id=article.articleId,
      url=article.url,
      authors=article.author,
      text=article.text,
      title=article.title,
    )

    if article.topic:
      a.topic = article.topic
    if article.parent_topic:
      a.parentTopic = article.parent_topic
    if article.publish_date:
      a.publish_date = article.publish_date
    if article.image:
       a.imageURL = article.image
    if article.polarization_score:
      a.polarizationScore = article.polarization_score
    if article.top_passage:
      a.topPassage = article.top_passage
    if article.top_fact:
      a.topFact = article.top_fact


  except Exception as e:
    logger.warn("Failed to fetch article from database")
    return FetchArticlesResponse(
      articleList=[],
      error=e,
    )

  return FetchArticlesResponse(
    articleList=[a],
    error=None,
  )


def fetchArticlesByUrl(articleUrls):
  """
    Will fetch articles by the article URL and populate the Article entity
  """
  hydratedArticles = []

  for url in articleUrls:
    try:
      article = ArticleModel.objects.get(url=url)
      fetchRes = articleResToModel(article)

      if fetchRes.error != None:
        logger.warn("Failed to fetch article with id")
        logger.warn(fetchRes.error)
        continue
      else:
        hydratedArticles.extend(fetchRes.articleList)
    except:
      logger.warn("Failed to fetch article with id")

  return FetchArticlesResponse(
    articleList=hydratedArticles,
    error=None,
  )


def queryArticles(queryArticleRequest):
  """
    Will query the article database using the queryArticleRequest and search for all rows where the given field is missing.
  """
  field = queryArticleRequest.field
  logger.info("Searching for rows with %s field empty", field)

  # Query for all records where the field is empty
  articles = []
  if field == "topic":
    articles = ArticleModel.objects.filter(topic="")
  elif field == "parent_topic":
    articles = ArticleModel.objects.filter(parent_topic="")
  elif field == "top_fact":
    articles = ArticleModel.objects.filter(top_fact="")
  elif field == "top_passage":
    articles = ArticleModel.objects.filter(top_passage="")
  elif field == "polarization_score":
    articles = ArticleModel.objects.filter(polarization_score=0)

  articleModels = []
  for article in articles:
    try:
      fetchRes = articleResToModel(article)

      if fetchRes.error != None:
        logger.warn("Failed to fetch article with id")
        logger.warn(fetchRes.error)
        continue
      else:
        articleModels.extend(fetchRes.articleList)
    except:
      logger.warn("Failed to fetch article with id")

  return QueryArticleResponse(
    articles=articleModels,
    error=None,
  )


