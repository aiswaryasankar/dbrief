from django.db import models

"""
  The topic page table will include the all the results from the getTopicPage call.
"""

class TopicPageModel(models.Model):
  class Meta:
    app_label = "topicFeed"

  topicPageId = models.AutoField(primary_key=True)
  topic = models.CharField(unique=True, max_length=255)
  topicId =  models.IntegerField("TopicId")
  summary = models.TextField("Text")
  title = models.TextField("Text")
  imageURL = models.TextField("Text")
  urls = models.TextField("Urls")
  topArticleId = models.IntegerField("TopArticleId")
  isTimeline = models.BooleanField("IsTimeline")
