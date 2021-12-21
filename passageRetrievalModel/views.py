from .serializers import *
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from .handler import *

"""
  This file will handle the actual external facing API for the passageRetrieval service. This includes mapping all the httpRequest / httpResponse objects to internal dataclass objects and performing the necessary validation steps that are specified in the serializers class. If there are any issues in this mapping / validation it will return an error immediately.  This file is necessary since service to service will make calls to the handler based on the dataclass request/ response whereas the front end will make requests through http which needs to be serialized from the JSON struct that's passed in.
"""

@api_view(['GET'])
def get_top_passage_view(request):
  """
    Get the top passage from the article and return it
  """
  req = GetTopPassageRequest(data=request.data)
  if not req.is_valid():
    return JsonResponse(req.errors)

  getTopPassageRequest = req.validated_data
  res = get_top_passage(getTopPassageRequest)

  return Response(res)


@api_view(['GET'])
def get_facts_view(request):
  """
    Get facts from the article and return a list of top facts
  """

  req = GetFactsRequest(data=request.data)
  if not req.is_valid():
    return JsonResponse(req.errors)

  getFactsRequest = req.validated_data
  res = get_facts(getFactsRequest)

  return Response(res)

