from django.db import models

class ArticleModel (models.Model):

  articleId = models.AutoField(primary_key=True)
  url = models.CharField("Url", unique=True, max_length=255)
  title = models.TextField("Title")
  text = models.TextField("Text")
  image = models.TextField("Image")
  publish_date = models.TextField("Publish Date", null=True, blank=True)
  author = models.TextField("Author")
  polarization = models.BooleanField("Polarity", default=0)


  def __str__(self):
    return self.url