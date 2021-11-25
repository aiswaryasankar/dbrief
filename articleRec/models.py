from django.db import models

class ArticleModel (models.Model):

  url = models.CharField("Url", primary_key=True, unique=True, max_length=255)
  title = models.TextField("Title")
  text = models.TextField("Text")
  image = models.TextField("Image")
  publish_date = models.TextField("Publish Date", null=True, blank=True)
  author = models.TextField("Author")


  def __str__(self):
    return self.url