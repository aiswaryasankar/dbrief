from django.db import models

class ArticleModel (models.Model):

  articleId = models.AutoField(primary_key=True)
  url = models.CharField("Url", unique=True, max_length=255)
  title = models.TextField("Title")
  text = models.TextField("Text")
  image = models.TextField("Image", null=True)
  publish_date = models.TextField("Publish Date", null=True)
  author = models.TextField("Author", null=True)
  polarization_score = models.FloatField("Polarity", default=0, null=True)
  topic = models.TextField("Topic", null=True)
  parent_topic = models.TextField("ParentTopic", null=True)
  top_passage = models.TextField("TopPassage", null=True)
  top_fact = models.TextField("TopFact", null=True)

  class Meta:
    app_label = "articleRec"

  def __str__(self):
    return self.url
