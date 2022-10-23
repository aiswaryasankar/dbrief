from .models import *
import logging
from idl import *
from logtail import LogtailHandler
from datetime import datetime, timedelta
import uuid

"""
  This file will include all the basic database CRUD operations including:
    - Save
    - Query
    - Delete
    - Update
"""

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)


def createLocationRepo(createLocationRequest):
  """
    Will create a location in the db
  """
  locationUUID = str(uuid.uuid1())

  try:
    location, created = LocationModel.objects.update_or_create(
      uuid = locationUUID,
      defaults={
        'name': createLocationRequest.name,
        'street': createLocationRequest.street,
        'city': createLocationRequest.city,
        'state': createLocationRequest.state,
        'zip': createLocationRequest.zip,
        'country': createLocationRequest.country,
      },
    )
    if created:
      logger.info('Saved location')

  except Exception as e:
    logger.warn("Failed to save location to the database: " + str(e))

    return CreateLocationResponse(locationUUID=None, location=None, error=e)

  return CreateLocationResponse(locationUUID=location.uuid, location=location, error=None)



def fetchLocationRepo(fetchLocationRequest):
  """
    Will fetch a location from the db given unique key of street
  """
  name = fetchLocationRequest.name
  street = fetchLocationRequest.street
  city = fetchLocationRequest.city

  try:
    locationRes = LocationModel.objects.get(street=street, city=city)

  except Exception as e:
    logger.warn("Failed to fetch location with street: " + str(street) + " " + str(city)  + " error: " + str(e))

    try:
      locationRes = LocationModel.objects.get(name=name)
    except Exception as e:
      logger.warn("Failed to fetch location with name: " + str(name) + " error: " + str(e))

      return FetchLocationResponse(
        uuid=None,
        location=None,
        error=e,
      )

  return FetchLocationResponse(
    uuid=locationRes.uuid,
    location=locationRes,
    error=None,
  )


def createOrganizationRepo(createOrganizationRequest):
  """
    Will save the organization to the database.
  """

  organizationUUID = str(uuid.uuid1())

  try:
    org, created = OrganizationModel.objects.update_or_create(
      uuid = organizationUUID,
      defaults={
        'name': createOrganizationRequest.name,
        'description': createOrganizationRequest.description,
        'image': createOrganizationRequest.image,
        'backgroundImage': createOrganizationRequest.backgroundImage,
        'locationUUID': createOrganizationRequest.locationUUID,
        'link': createOrganizationRequest.link,
      },
    )
    if created:
      logger.info('Saved organization')

  except Exception as e:
    logger.warn("Failed to save organization to the database: " + str(e))

    return CreateOrganizationResponse(organizationUUID=None, organization=None, error=e)

  return CreateOrganizationResponse(organizationUUID=org.uuid, organization=org, error=None)



