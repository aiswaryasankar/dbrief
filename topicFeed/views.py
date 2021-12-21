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

@api_view(['GET'])
def GetTopicPage(request):
  """
    This function will map the request params of url, articleID, topic string or search string to the appropriate field and pass it to the controller to hydrate the page appropriately. It will execute the following in order to hydrate the TopicPage struct:
  """
  req = GetTopicPageByURLRequest(data=request.data)
  if not req.is_valid():
    return JsonResponse(req.errors)

  getDocumentTopicRequest = req.validated_data
  res = get_document_topic(getDocumentTopicRequest)

  return Response(res)



@api_view(['GET'])
def WhatsHappening(request):
  """
    Get's a list of the topic articles for the day
  """
  req = GetDocumentTopicRequest(data=request.data)
  if not req.is_valid():
    return JsonResponse(req.errors)

  getDocumentTopicRequest = req.validated_data
  res = get_document_topic(getDocumentTopicRequest)

  return Response(res)


@api_view(['GET'])
def GetRecommendedTopicsForUser(request):
  """
    Gets a list of the recommended topics for a given user
  """
  req = GetDocumentTopicRequest(data=request.data)
  if not req.is_valid():
    return JsonResponse(req.errors)

  getDocumentTopicRequest = req.validated_data
  res = get_document_topic(getDocumentTopicRequest)

  return Response(res)


@api_view(['GET'])
def GetTopicsYouFollow(request):
  """
    Gets a list of the topics a user follows
  """
  req = GetDocumentTopicRequest(data=request.data)
  if not req.is_valid():
    return JsonResponse(req.errors)

  getDocumentTopicRequest = req.validated_data
  res = get_document_topic(getDocumentTopicRequest)

  return Response(res)




