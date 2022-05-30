from django.db import models

class NewsletterConfigModel (models.Model):
  class Meta:
    app_label = "newsletter"

  newsletterConfigId = models.AutoField(primary_key=True)
  userId = models.IntegerField("UserId", unique=True)
  firebaseUserId = models.TextField("FirebaseUserId", null=True)
  deliveryTime = models.TextField("Delivery time", default="EVENING")
  recurrenceType = models.TextField("Recurrence type", default="WEEKLY")
  dayOfWeek = models.IntegerField("Day of week", default=0)
  isEnabled = models.BooleanField("Is Enabled", default=True)

  def __str__(self):
    return str(self.newsletterConfigId) + " " + str(self.userId)
