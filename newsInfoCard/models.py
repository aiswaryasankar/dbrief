from django.db import models
from datetime import datetime

"""
  All data models for the newsInfoCard service including the NewsInfoCard and the OpinionCard.
"""

class NewsInfoCardModel (models.Model):

  id = models.AutoField(primary_key=True)
  uuid = models.CharField("UUID", unique=True, max_length=36)
  url = models.CharField("Url", unique=True, max_length=255)
  title = models.TextField("Title", null=True)
  summary = models.TextField("Summary", null=True)
  image = models.TextField("Image", null=True)
  publish_date = models.TextField("Publish Date", null=True)
  author = models.TextField("Author", null=True)
  source = models.TextField("Source", null=True)
  is_political = models.BooleanField("IsPolitical", default=0, null=True)
  topic = models.TextField("Topic", null=True)
  leftOpinionCardUUID = models.CharField("LeftOpinionCardUUID", max_length=36, null=True)
  rightOpinionCardUUID = models.CharField("RightOpinionCardUUID", max_length=36, null=True)
  articleUrlList = models.TextField("ArticleUrlList", null=True)
  articleTitleList = models.TextField("ArticleTitleList", null=True)
  createdAt = models.TextField("CreatedAt", default=datetime.now)

  class Meta:
    app_label = "newsInfoCard"

  def __str__(self):
    return self.uuid


class OpinionCardModel (models.Model):

  id = models.AutoField(primary_key=True)
  uuid = models.CharField("UUID", unique=True, max_length=36)
  summary = models.TextField("Summary", null=True)
  articleUrlList = models.TextField("ArticleUrlList", null=True)
  articleTitleList = models.TextField("ArticleTitleList", null=True)

  class Meta:
    app_label = "newsInfoCard"

  def __str__(self):
    return self.uuid

