from django.db import models

"""
  The user table will include the topic id, topic and parent topic
"""
class TopicModel (models.Model):

  topicId = models.AutoField(primary_key=True)
  topic = models.TextField("Topic")
  parentTopic = models.TextField("Parent topic")

  def __str__(self):
    return self.topic + ":" + self.parentTopic
