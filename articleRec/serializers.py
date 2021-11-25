from rest_framework import serializers
from .models import ArticleModel


class ArticleSerializer(serializers.ModelSerializer):

  class Meta:
    model = ArticleModel
    app_label = "articleRec.models.ArticleModel"
    fields = ['pk', 'title', 'url', 'text']
    db_table = "articleModel"
