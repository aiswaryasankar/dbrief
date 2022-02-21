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

  def __str__(self):
    return self.topic + ":" + self.parentTopic
