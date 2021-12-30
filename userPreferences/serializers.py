from rest_framework import serializers
from idl import *
from rest_framework_dataclasses.serializers import DataclassSerializer

"""
  This file will define all the Serializers for the userPreferences service.  Serializers serve to map and handle validation between httpRequest objects passed into the service and the dataclasses used to store and pass data around internally between the various apps.
"""

class CreateUserRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = CreateUserRequest

class GetUserRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = GetUserRequest

class FollowTopicRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = FollowTopicRequest

class UnfollowTopicRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = UnfollowTopicRequest

class GetTopicsForUserRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = GetTopicsForUserRequest

class GetRecommendedTopicsForUserRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = GetRecommendedTopicsForUserRequest



