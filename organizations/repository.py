from .models import *
import logging
from idl import *
from logtail import LogtailHandler
from datetime import datetime, timedelta
import uuid
from .mapper import *

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




