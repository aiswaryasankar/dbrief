from .serializers import *
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from .handler import *
from idl import *

"""
  This file will handle the actual external facing API for the homeFeed service. This includes mapping all the httpRequest / httpResponse objects to internal dataclass objects and performing the necessary validation steps that are specified in the serializers class. If there are any issues in this mapping / validation it will return an error immediately.  This file is necessary since service to service will make calls to the handler based on the dataclass request/ response whereas the front end will make requests through http which needs to be serialized from the JSON struct that's passed in.
"""

@api_view(['POST'])
def hydrate_home_page_view(request):
  """
    This function will map the request params of url, articleID, topic string or search string to the appropriate field and pass it to the controller to hydrate the page appropriately. It will execute the following in order to hydrate the TopicPage struct:
  """
  req = HydrateHomePageCachedSerializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  hydrateHomePageRequest = req.validated_data
  res = hydrateHomePage(hydrateHomePageRequest)

  return Response(res.to_json())


@api_view(['POST'])
def hydrate_home_page_cached_view(request):
  """
    This function will map the request params of url, articleID, topic string or search string to the appropriate field and pass it to the controller to hydrate the page appropriately. It will execute the following in order to hydrate the TopicPage struct:
  """
  print("Calling cached view")
  req = HydrateHomePageCachedSerializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  hydrateHomePageRequest = req.validated_data
  res = hydrateHomePageCached(hydrateHomePageRequest)

  return Response(res.to_json())

