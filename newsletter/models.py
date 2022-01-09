from django.db import models

class NewsletterConfigModel (models.Model):

  newsletterConfigId = models.AutoField(primary_key=True)
  userId = models.IntegerField("UserId")
  deliveryTime = models.CharField("Delivery time")
  dayOfWeek = models.IntegerField("Day of week")
  isEnabled = models.BooleanField("Is Enabled")

  def __str__(self):
    return self.url


