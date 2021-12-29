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
  req = GetTopicPageByURLRequestSerializer(data=request.data)
  if not req.is_valid():
    return JsonResponse(req.errors)

  getTopicPageByURLRequest = req.validated_data
  res = getTopicPage(getTopicPageByURLRequest)

  return Response(res.to_json())



@api_view(['POST'])
def whats_happening_view(request):
  """
    Get's a list of the topic articles for the day
  """
  req = WhatsHappeningRequestSerializer(data=request.data)
  if not req.is_valid():
    return JsonResponse(req.errors)

  whatsHappeningRequest = req.validated_data
  res = whatsHappening(whatsHappeningRequest)

  return Response(res)


@api_view(['POST'])
def get_recommended_topics_for_user_view(request):
  """
    Gets a list of the recommended topics for a given user
  """
  req = GetRecommendedTopicsForUserRequestSerializer(data=request.data)
  if not req.is_valid():
    return JsonResponse(req.errors)

  getRecommendedTopicsForUserRequest = req.validated_data
  res = getRecommendedTopicsForUser(getRecommendedTopicsForUserRequest)

  return Response(res)


@api_view(['POST'])
def get_topics_you_follow_view(request):
  """
    Gets a list of the topics a user follows
  """
  req = GetTopicsForUserRequestSerializer(data=request.data)
  if not req.is_valid():
    return JsonResponse(req.errors)

  getTopicsForUserRequest = req.validated_data
  res = getTopicsYouFollow(getTopicsForUserRequest)

  return Response(res)



