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


@api_view(['POST'])
def hello_world_view(request):
  """
    Demo function for testing purposes
  """
  req = HelloWorldRequestSerializer(data=request.data)
  if not req.is_valid():
    return JsonResponse(req.errors)

  helloWorldRequest = req.validated_data
  res = hello_world(helloWorldRequest)

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


@api_view(['GET'])
def hydrate_article_view(request):
  """
    Will scrape and hydrate the url passed in and return the result as an Article model object
  """
  req = HydrateArticleRequestSerializer(data=request.data)
  if not req.is_valid():
    return JsonResponse(req.errors)

  hydrateArticleRequest = req.validated_data

  res = hydrate_article(hydrateArticleRequest)

  return Response(res.to_json())


@api_view(['GET'])
def populate_articles_batch_view(request):
  """
    Will populate all the articles in batch and return stats on the number of articles successfully populated in the db.
  """
  res = populate_articles_batch()
  #TODO: add response validation when converting from dataclass to JSON
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

