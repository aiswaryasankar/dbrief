from rest_framework import serializers
from idl import *
from rest_framework_dataclasses.serializers import DataclassSerializer
from rest_framework.parsers import JSONParser

"""
  This file will define all the Serializers for the topicModeling service.  Serializers serve to map and handle validation between httpRequest objects passed into the service and the dataclasses used to store and pass data around internally between the various apps.
"""

class SearchDocumentsByTopicRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = SearchDocumentsByTopicRequest

class SearchTopicsRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = SearchTopicsRequest

class AddDocumentRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = AddDocumentRequest

class QueryDocumentsRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = QueryDocumentsRequest

class TrainAndIndexTopicModelRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = TrainAndIndexTopicModelRequest

class QueryDocumentsRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = QueryDocumentsRequest

class GetDocumentTopicRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = GetDocumentTopicRequest

class DeleteTopicsRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = DeleteTopicsRequest

###
#
# TopicModelingV2 endpoints
#
###

class GetDocumentTopicRequestV2Serializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = GetDocumentTopicRequestV2

class SearchTopicsRequestV2Serializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = SearchTopicsRequestV2


