from rest_framework import serializers
from idl import *
from rest_framework_dataclasses.serializers import DataclassSerializer
from rest_framework.parsers import JSONParser

"""
  This file will define all the Serializers for the topicFeed service.  Serializers serve to map and handle validation between httpRequest objects passed into the service and the dataclasses used to store and pass data around internally between the various apps.
"""

class GetTopicPageByURLRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = GetTopicPageByURLRequest

class GetTopicPageByArticleIDRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = GetTopicPageByArticleIDRequest

class GetTopicPageBySearchStringRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = GetTopicPageBySearchStringRequest

class GetTopicPageByTopicIDRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = GetTopicPageByTopicIDRequest

class WhatsHappeningRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = WhatsHappeningRequest

