from .serializers import *
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from .handler import *
from idl import *

"""
  This file will handle the actual external facing API for the topicFeed service. This includes mapping all the httpRequest / httpResponse objects to internal dataclass objects and performing the necessary validation steps that are specified in the serializers class. If there are any issues in this mapping / validation it will return an error immediately.  This file is necessary since service to service will make calls to the handler based on the dataclass request/ response whereas the front end will make requests through http which needs to be serialized from the JSON struct that's passed in.
"""

@api_view(['POST'])
def get_topic_page_view(request):
  """
    This function will map the request params of url, articleID, topic string or search string to the appropriate field and pass it to the controller to hydrate the page appropriately. It will execute the following in order to hydrate the TopicPage struct:
  """
  req = GetTopicPageRequestSerializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  getTopicPageRequest = req.validated_data
  res = getTopicPage(getTopicPageRequest)

  return Response(res.to_json())



@api_view(['POST'])
def whats_happening_view(request):
  """
    Get's a list of the topic articles for the day
  """
  req = WhatsHappeningRequestSerializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  # whatsHappeningRequest = req.validated_data
  # res = whatsHappening(whatsHappeningRequest)

  whatsHappeningRequest = req.validated_data
  res = whatsHappeningV2(whatsHappeningRequest)

  return Response(res.to_json())


@api_view(['POST'])
def hydrate_topic_pages_view(request):
  """
    This function will be run by a cron job to hydrate all the topic pages.
  """
  res = hydrateTopicPages()

  return Response(res.to_json())





