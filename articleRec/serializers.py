from rest_framework import serializers
from .models import ArticleModel
from idl import *
from rest_framework_dataclasses.serializers import DataclassSerializer

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
  class Meta:
    dataclass = HelloWorldRequest

class PopulateArticleRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = PopulateArticleRequest

class SaveArticleRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = SaveArticleRequest

class FetchArticlesRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = FetchArticlesRequest

class HydrateArticleRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = HydrateArticleRequest

