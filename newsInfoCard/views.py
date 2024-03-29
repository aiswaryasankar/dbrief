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


@api_view(['POST'])
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


@api_view(['POST'])
def create_news_info_card_backfill_view(request):
  """
    Create backfill for last x days of newsInfoCards
  """

  req = CreateNewsInfoCardBackfillRequestSerializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  createNewsInfoCardBackfillRequest = req.validated_data

  res = createNewsInfoCardBackfill(createNewsInfoCardBackfillRequest)

  return Response(res.to_json())


@api_view(['POST'])
def set_user_engagement_for_news_info_card_view(request):
  """
    Set user engagement for news info card
  """

  req = SetUserEngagementForNewsInfoCardRequestSerializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  setUserEngagementForNewsInfoCardRequest = req.validated_data

  res = setUserEngagementForNewsInfoCard(setUserEngagementForNewsInfoCardRequest)

  return Response(res.to_json())

