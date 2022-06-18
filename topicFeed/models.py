from django.db import models
from datetime import datetime

"""
  The topic page table will include the all the results from the getTopicPage call.
"""

class TopicPageModel(models.Model):
  class Meta:
    app_label = "topicFeed"

  topicPageId = models.AutoField(primary_key=True)
  topic = models.CharField(max_length=255)
  topicId =  models.IntegerField("TopicId")
  summary = models.TextField("Text")
  title = models.TextField("Text")
  imageURL = models.TextField("Text")
  urls = models.TextField("Urls")
  topArticleId = models.IntegerField("TopArticleId")
  isTimeline = models.BooleanField("IsTimeline")
  createdAt = models.TextField("CreatedAt", default=datetime.now)



