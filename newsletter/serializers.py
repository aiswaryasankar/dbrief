from rest_framework import serializers
from idl import *
from rest_framework_dataclasses.serializers import DataclassSerializer
from rest_framework.parsers import JSONParser

"""
  This file will define all the Serializers for the newsletter service.  Serializers serve to map and handle validation between httpRequest objects passed into the service and the dataclasses used to store and pass data around internally between the various apps.
"""


class CreateNewsletterConfigForUserRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = CreateNewsletterConfigForUserRequest

class GetNewsletterConfigForUserRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = GetNewsletterConfigForUserRequest

class UpdateNewsletterConfigForUserRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = UpdateNewsletterConfigForUserRequest

class HydrateNewsletterRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = HydrateNewsletterRequest

class SendNewsletterRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = SendNewsletterRequest

class SendNewslettersBatchRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = SendNewslettersBatchRequest
