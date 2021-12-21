from django.db import models

class ArticleModel (models.Model):

  articleId = models.AutoField(primary_key=True)
  url = models.CharField("Url", unique=True, max_length=255)
  title = models.TextField("Title")
  text = models.TextField("Text")
  image = models.TextField("Image", null=True)
  publish_date = models.TextField("Publish Date", null=True, blank=True)
  author = models.TextField("Author", null=True)
  polarization_score = models.FloatField("Polarity", default=0, null=True)
  primary_topic = models.TextField("PrimaryTopic", null=True)
  sub_topic = models.TextField("SubTopic", null=True)

  def __str__(self):
    return self.url


