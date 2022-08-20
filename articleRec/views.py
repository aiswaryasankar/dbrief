from rest_framework import generics
from .serializers import *
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from .handler import *

"""
  This file will handle the actual external facing API for the articleRec service. This includes mapping all the httpRequest / httpResponse objects to internal dataclass objects and performing the necessary validation steps that are specified in the serializers class. If there are any issues in this mapping / validation it will return an error immediately.  This file is necessary since service to service will make calls to the handler based on the dataclass request/ response whereas the front end will make requests through http which needs to be serialized from the JSON struct that's passed in.
"""

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = []
logger.addHandler(handler)
logger.setLevel(logging.INFO)

@api_view(['POST'])
def hello_world_view(request):
  """
    Demo function for testing purposes
  """
  req = HelloWorldRequestSerializer(data=request.data)
  logger.info("request")
  logger.info(req)
  if not req.is_valid():
    logger.info("req not valid")
    logger.info(req.errors)
    return JsonResponse(req.errors)

  logger.info("req valid")
  helloWorldRequest = req.validated_data
  logger.info(req.data)
  logger.info(req.validated_data)
  res = hello_world(helloWorldRequest)
  logger.info("res")
  logger.info(res)
  return Response(res.to_json())


@api_view(['GET'])
def fetch_articles_view(request):
  """
    Given a list of articleIds, this will return the entire hydrated article entity in the db for the batch of articles.  If no articleIds are provided, it will return all articles in the database.
  """
  req = FetchArticlesRequestSerializer(data=request.data)
  if not req.is_valid():
    return JsonResponse(req.errors)

  fetchArticlesRequest = req.validated_data

  res = fetch_articles(fetchArticlesRequest)

  return Response(res.to_json())


@api_view(['POST'])
def hydrate_article_view(request):
  """
    Will scrape and hydrate the url passed in and return the result as an Article model object
  """
  req = HydrateArticleRequestSerializer(data=request.data)
  if not req.is_valid():
    return JsonResponse(req.errors)

  hydrateArticleRequest = req.validated_data

  res = hydrate_article(hydrateArticleRequest)

  # Setting article to None since it is of type Newspaper Article
  res.article=None

  return Response(res.to_json())


@api_view(['GET'])
def populate_articles_batch_view(request):
  """
    Will populate all the articles in batch and return stats on the number of articles successfully populated in the db.
  """
  res = populate_articles_batch_v1()
  return Response(res.to_json())


@api_view(['GET'])
def populate_articles_batch_v2_view(request):
  """
    This endpoint calls the batch v2 populate articles endpoint optimized for SPEED and MEMORY.
  """
  res = populate_articles_batch_v2()
  return Response(res.to_json())


@api_view(['GET'])
def populate_articles_and_document_store_batch_v2_view(request):
  """
    This endpoint calls the batch v2 populate articles endpoint optimized for SPEED and MEMORY and also appends the articles to a document store
    for better search.
  """
  res = populate_articles_and_document_store_batch_v2()
  return Response(res.to_json())


@api_view(['POST'])
def populate_article_by_url_view(request):
  """
    Populates a single article based on the request.url
  """
  req = PopulateArticleRequestSerializer(data=request.data)

  if not req.is_valid():
    return JsonResponse(req.errors)

  populateArticleRequest = req.validated_data
  res = populate_article_by_url(populateArticleRequest)

  return Response(res.to_json())


@api_view(['POST'])
def article_backfill_view(request):
  """
    This endpoint will function for a few different use cases. First it will be run daily as a way to backfill any missing data in the article database. This includes all fields that are missing. Additionally it can function to update fields even if they were already populated. This would primarily be used for topic regeneration based on an updated model. Thus the request will either take in force_update, as well as a list of fields to update.  If neither are provided it will batch update all fields that are missing.
  """

  req = ArticleBackfillRequestSerializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  articleBackfillRequest = req.validated_data

  res = article_backfill(articleBackfillRequest)

  return Response(res.to_json())


@api_view(['POST'])
def delete_articles_view(request):
  """
    This endpoint will delete articles that are past the number of days prior to the current day.
  """

  req = DeleteArticlesRequestSerializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  deleteArticlesRequest = req.validated_data

  print(deleteArticlesRequest)
  res = delete_articles(deleteArticlesRequest)

  return Response(res.to_json())


