from rest_framework import serializers
from idl import *
from rest_framework_dataclasses.serializers import DataclassSerializer

"""
  This file will define all the Serializers for the passageRetrievalModel service.  Serializers serve to map and handle validation between httpRequest objects passed into the service and the dataclasses used to store and pass data around internally between the various apps.
"""

class GetFactsRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = SearchDocumentsByTopicRequest

class GetTopPassageRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = SearchTopicsRequest
