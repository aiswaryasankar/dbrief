from idl import GetMDSSummaryRequest
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
def get_mds_summary_view(request):
  """
    Get the the MDS summary using GPT-3 from the collection of articles passed in
  """
  req = GetMDSSummaryRequest(data=request.data)
  if not req.is_valid():
    return JsonResponse(req.errors)

  GetMDSSummaryResponse = req.validated_data
  res = get_mds_summary_handler(GetMDSSummaryResponse)

  return Response(res)


@api_view(['GET'])
def get_mds_summary_v2_view(request):
  """
    This calls the "smarter" extractive MDS model to do it by sentences instead of using the GPT API for this.
  """
  req = GetMDSSummaryRequest(data=request.data)
  if not req.is_valid():
    return JsonResponse(req.errors)

  getMDSSummaryRequest = req.validated_data
  res = get_mds_summary_v2_handler(getMDSSummaryRequest)

  return Response(res)


@api_view(['GET'])
def get_mds_summary_v3_view(request):
  """
    This calls the "smartest" MDS model by first extracting the top passages from each of the articles, then creating a MDS summary using the pegasus model from each of the top passages.
  """

  req = GetMDSSummaryRequest(data=request.data)
  if not req.is_valid():
    return JsonResponse(req.errors)

  getMDSSummaryRequest = req.validated_data
  res = get_mds_summary_v3_handler(getMDSSummaryRequest)

  return Response(res)


