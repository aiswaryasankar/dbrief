from rest_framework import serializers
from idl import *
from rest_framework_dataclasses.serializers import DataclassSerializer
from rest_framework.parsers import JSONParser

"""
  This file will define all the Serializers for the homeFeed service.  Serializers serve to map and handle validation between httpRequest objects passed into the service and the dataclasses used to store and pass data around internally between the various apps.
"""

class HydrateHomePageSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = HydrateHomePageRequest

# Both requests have the same input, renamed for clarity
class HydrateHomePageCachedSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = HydrateHomePageRequest
