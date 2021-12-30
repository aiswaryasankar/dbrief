from rest_framework import generics
from .serializers import *
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from .handler import *
from logtail import LogtailHandler
import logging

"""
  This file will handle the actual external facing API for the articleRec service. This includes mapping all the httpRequest / httpResponse objects to internal dataclass objects and performing the necessary validation steps that are specified in the serializers class. If there are any issues in this mapping / validation it will return an error immediately.  This file is necessary since service to service will make calls to the handler based on the dataclass request/ response whereas the front end will make requests through http which needs to be serialized from the JSON struct that's passed in.
"""

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = []
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@api_view(['POST'])
def create_user_view(request):
  """
    Creates a user in the database
  """
  req = CreateUserRequestSerializer(data=request.data)

  if not req.is_valid():
    return JsonResponse(req.errors)

  createUserRequest = req.validated_data
  res = create_user(createUserRequest)

  return Response(res.to_json())


@api_view(['POST'])
def get_user_view(request):
  """
    Gets a user from the database
  """
  req = GetUserRequestSerializer(data=request.data)

  if not req.is_valid():
    return JsonResponse(req.errors)

  getUserRequest = req.validated_data
  res = get_user(getUserRequest)

  return Response(res.to_json())


@api_view(['POST'])
def follow_topic_view(request):
  """
    Gets a user to follow a topic
  """
  req = FollowTopicRequestSerializer(data=request.data)

  if not req.is_valid():
    return JsonResponse(req.errors)

  followTopicRequest = req.validated_data
  res = follow_topic(followTopicRequest)

  return Response(res.to_json())


@api_view(['POST'])
def unfollow_topic_view(request):
  """
    Gets a user to unfollow a topic
  """
  req = UnfollowTopicRequestSerializer(data=request.data)

  if not req.is_valid():
    return JsonResponse(req.errors)

  unfollowTopicRequest = req.validated_data
  res = unfollow_topic(unfollowTopicRequest)

  return Response(res.to_json())


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

