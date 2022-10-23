from django.db import models
from datetime import datetime

"""
  All data models for the organization service including the Organization, Location and UserOrgAssociation
"""

class OrganizationModel (models.Model):

  id = models.AutoField(primary_key=True)
  uuid = models.CharField("UUID", unique=True, max_length=36)
  name = models.TextField("Name", unique=True)
  image = models.TextField("Image", null=True)
  backgroundImage = models.TextField("BackgroundImage", null=True)
  description = models.TextField("Description", null=True)
  locationUUID = models.CharField("LocationUUID", max_length=36)
  createdAt = models.TextField("CreatedAt", default=datetime.now)

  class Meta:
    app_label = "organizations"

  def __str__(self):
    return self.uuid



class LocationModel (models.Model):

  id = models.AutoField(primary_key=True)
  uuid = models.CharField("UUID", unique=True, max_length=36)
  street = models.TextField("Street", null=True)
  city = models.TextField("City", null=True)
  state = models.TextField("State", null=True)
  zip = models.TextField("Zip", null=True)
  country = models.TextField("Country", null=True)

  class Meta:
    app_label = "organizations"

  def __str__(self):
    return self.street + " " + self.city + ", " + self.state



