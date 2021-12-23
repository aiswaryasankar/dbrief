from rest_framework import serializers
from idl import *
from rest_framework_dataclasses.serializers import DataclassSerializer

"""
  This file will define all the Serializers for the topicFeed service.  Serializers serve to map and handle validation between httpRequest objects passed into the service and the dataclasses used to store and pass data around internally between the various apps.
"""

class GetTopicPageByURLRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = GetTopicPageByURLRequest

class GetTopicPageByArticleIDRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = GetTopicPageByArticleIDRequest

class GetTopicPageBySearchStringRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = GetTopicPageBySearchStringRequest

class GetTopicPageByTopicIDRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = GetTopicPageByTopicIDRequest

class WhatsHappeningRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = WhatsHappeningRequest

class GetTopicsForUserRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = GetTopicsForUserRequest

class GetRecommendedTopicsForUserRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = GetRecommendedTopicsForUserRequest
