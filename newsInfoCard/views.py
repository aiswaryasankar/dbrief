from django.shortcuts import render
from .serializers import *
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from .handler import *
from idl import *


@api_view(['POST'])
def create_news_info_card_view(request):
  """
    Creates a news info card for a given article
  """
  req = CreateNewsInfoCardRequestSerializer(data=request.data)

  if not req.is_valid():
    return JsonResponse(req.errors)

  createNewsInfoCardRequest = req.validated_data
  res = createNewsInfoCard(createNewsInfoCardRequest)

  return Response(res.to_json())


@api_view(['POST'])
def create_news_info_card_batch_view(request):
  """
    Create a batch of news info cards based on all the new articles that are being hydrated
  """

  req = CreateNewsInfoCardBatchRequestSerializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  createNewsInfoCardBatchRequest = req.validated_data

  res = createNewsInfoCardBatch(createNewsInfoCardBatchRequest)

  return Response(res.to_json())


@api_view(['GET'])
def fetch_news_info_card_batch_view(request):
  """
    Fetch a batch of news info cards for the given day
  """

  req = FetchNewsInfoCardBatchRequestSerializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  fetchNewsInfoCardBatchRequest = req.validated_data

  res = fetchNewsInfoCardBatch(fetchNewsInfoCardBatchRequest)

  return Response(res.to_json())

