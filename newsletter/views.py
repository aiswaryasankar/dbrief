from .serializers import *
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from .handler import *
from idl import *

"""
  This file will handle the actual external facing API for the newsletter service.
  This includes mapping all the httpRequest / httpResponse objects to internal
  dataclass objects and performing the necessary validation steps that are specified
  in the serializers class. If there are any issues in this mapping / validation it will
  return an error immediately.  This file is necessary since service to service will make
  calls to the handler based on the dataclass request/ response whereas the front end will
  make requests through http which needs to be serialized from the JSON struct that's passed in.
"""


@api_view(['POST'])
def create_newsletter_config_for_user_view(request):
  """
    Create a newsletter config for a user
  """
  req = CreateNewsletterConfigForUserRequestSerializer(data=request.data)
  if not req.is_valid():
    print(req.errors)
    return Response(req.errors)

  print(req.validated_data)
  createNewsletterConfigForUserRequest = req.validated_data
  res = create_newsletter_config_for_user(createNewsletterConfigForUserRequest)

  return Response(res.to_json())


@api_view(['POST'])
def update_newsletter_config_for_user_view(request):
  """
    Update a newsletter config for a user
  """
  req = UpdateNewsletterConfigForUserRequestSerializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  updateNewsletterConfigForUserRequest = req.validated_data
  res = update_newsletter_config_for_user(updateNewsletterConfigForUserRequest)

  return Response(res.to_json())


@api_view(['POST'])
def get_newsletter_config_for_user_view(request):
  """
    Get a newsletter config for a user
  """
  req = GetNewsletterConfigForUserRequestSerializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  getNewsletterConfigForUserRequest = req.validated_data
  res = get_newsletter_config_for_user(getNewsletterConfigForUserRequest)

  return Response(res.to_json())


@api_view(['POST'])
def send_newsletters_batch_view(request):
  """
    Send a batch of newsletters that match the current time
  """
  req = SendNewslettersBatchRequestSerializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  sendNewslettersBatchRequest = req.validated_data
  res = send_newsletters_batch(sendNewslettersBatchRequest)

  return Response(res.to_json())


@api_view(['POST'])
def send_newsletter_view(request):
  """
   Send a newsletter to the specified user
  """
  req = SendNewsletterRequestSerializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  sendNewsletterRequest = req.validated_data
  res = send_newsletter(sendNewsletterRequest)

  return Response(res.to_json())


@api_view(['POST'])
def hydrate_newsletter_view(request):
  """
    Hydrate a newsletter for a user
  """
  req = HydrateNewsletterRequestSerializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  hydrateNewsletterRequest = req.validated_data
  res = hydrate_newsletter(hydrateNewsletterRequest)

  return Response(res.to_json())


