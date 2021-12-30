from django.db import models

"""
  The user table will include the user's email, name, id, username and possibly firebaseAuthId
"""
class UserModel (models.Model):

  userId = models.AutoField(primary_key=True)
  firstName = models.TextField("First name")
  lastName = models.TextField("Title")
  email = models.TextField("Text")
  firebaseAuthId = models.TextField("Image", null=True)

  def __str__(self):
    return self.firstName + " " + self.lastName


"""
  The userTopic table will store a list of all topics that each user follows associated by user and topic ids
"""
class UserTopicModel (models.Model):

  userTopicId = models.AutoField(primary_key=True)
  userId = models.TextField("UserId")
  topic = models.TextField("Topic")

  def __str__(self):
    return self.userId + " " + self.topic

