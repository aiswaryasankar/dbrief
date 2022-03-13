from django.db import models

class ArticleModel (models.Model):

  articleId = models.AutoField(primary_key=True)
  url = models.CharField("Url", unique=True, max_length=255)
  title = models.TextField("Title")
  text = models.TextField("Text")
  image = models.TextField("Image")
  publish_date = models.TextField("Publish Date", null=True)
  author = models.TextField("Author")
  polarization_score = models.FloatField("Polarity", default=0)
  topic = models.TextField("Topic")
  parent_topic = models.TextField("ParentTopic")
  top_passage = models.TextField("TopPassage")
  top_fact = models.TextField("TopFact")

  class Meta:
    app_label = "articleRec"

  def __str__(self):
    return self.url



