from rest_framework import serializers
from .models import ArticleModel
from idl import *
from rest_framework_dataclasses.serializers import DataclassSerializer
from rest_framework.parsers import JSONParser

"""
  This file will define all the Serializers for the articleRec service.  Serializers serve to map and handle validation between httpRequest objects passed into the service and the dataclasses used to store and pass data around internally between the various apps.
"""

class ArticleSerializer(serializers.ModelSerializer):

  class Meta:
    model = ArticleModel
    app_label = "articleRec.models.ArticleModel"
    fields = ['pk', 'title', 'url', 'text']
    db_table = "articleModel"

class HelloWorldRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = HelloWorldRequest

class PopulateArticleRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = PopulateArticleRequest

class SaveArticleRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = SaveArticleRequest

class FetchArticlesRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = FetchArticlesRequest

class HydrateArticleRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = HydrateArticleRequest

class ArticleBackfillRequestSerializer(DataclassSerializer):
  parser_classes = JSONParser
  class Meta:
    dataclass = ArticleBackfillRequest

