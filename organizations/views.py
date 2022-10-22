from django.shortcuts import render
from .serializers import *
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from .handler import *
from idl import *


@api_view(['POST'])
def create_organization_view(request):
  """
    Creates an organization
  """
  req = CreateOrganizationRequestSerializer(data=request.data)

  if not req.is_valid():
    return JsonResponse(req.errors)

  createOrganizationRequest = req.validated_data
  res = createOrganization(createOrganizationRequest)

  return Response(res.to_json())


@api_view(['POST'])
def generate_recommended_orgs_for_news_info_card_view(request):
  """
    Generate recommended orgs for a news info card
  """
  req = GenerateRecommendedOrgsForNewsInfoCardRequestSerializer(data=request.data)

  if not req.is_valid():
    return JsonResponse(req.errors)

  generateRecommendedOrgsForNewsInfoCardRequest = req.validated_data
  res = generateRecommendedOrgsForNewsInfoCard(generateRecommendedOrgsForNewsInfoCardRequest)

  return Response(res.to_json())




