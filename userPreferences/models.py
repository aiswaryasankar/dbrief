from django.db import models

"""
  The user table will include the user's email, name, id, username and possibly firebaseAuthId
"""
class UserModel (models.Model):
  class Meta:
    app_label = "userPreferences"

  userId = models.AutoField(primary_key=True)
  firstName = models.TextField("First name")
  lastName = models.TextField("Title")
  email = models.CharField("Email", unique=True, max_length=255)
  firebaseAuthId = models.TextField("FirebaseAuthId", null=True)

  def __str__(self):
    return self.firstName + " " + self.lastName


"""
  The userTopic table will store a list of all topics that each user follows associated by user and topic ids
"""
class UserTopicModel (models.Model):
  class Meta:
    unique_together = (('userId', 'topicId'),)
    app_label = "userPreferences"

  userTopicId = models.AutoField(primary_key=True)
  userId = models.IntegerField("UserId", null=True)
  topicId = models.IntegerField("TopicId", null=True)
  forNewsletter = models.BooleanField("For Newsletter", default=False)

  def __str__(self):
    return str(self.userId) + " " + str(self.topicId)
