from django.db import models

"""
  The user table will include the topic id, topic and parent topic
"""
class TopicModel (models.Model):
  class Meta:
    unique_together = (('topic', 'parentTopic'),)
    app_label = "topicModeling"

  topicId = models.AutoField(primary_key=True)
  topic = models.CharField("Topic", max_length=255)
  parentTopic = models.CharField("Parent topic", max_length=255)
  createdAt = models.TextField("Publish Date", null=True)

  def __str__(self):
    return self.topic + ":" + self.parentTopic


class TopicPageModel(models.Model):
  class Meta:
    app_label = "topicPage"

  topic = models.CharField("Topic", max_length=255)
  topicId =  models.AutoField(primary_key=True)
  summary = models.TextField("Text")
  title = models.TextField("Text")
  imageURL = models.TextField("Text")
  facts = models.TextField("Text")
  opinions = models.TextField("Text")
  # topArticleId =
  # isTimeline =


