"""
  This service is primarily responsible for creating new organizations.
"""

import logging
from articleRec import handler as articleRecHandler
from mdsModel import handler as mdsHandler
from topicFeed import handler as topicFeedHandler
from .repository import *
from topicModeling import handler as tpHandler
from mdsModel.handler import *
from datetime import datetime
import idl
import threading
import random
from multiprocessing.pool import ThreadPool, Pool

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)



def createOrganization(createOrganizationRequest):
  """
    This function will create an organization
  """

  if createOrganizationRequest.name == None:
    return CreateOrganizationResponse(
      organizationUUID=None,
      organization=None,
      error="Organization is missing a name"
    )

  if createOrganizationRequest.url == None:
    return CreateOrganizationResponse(
      organizationUUID=None,
      organization=None,
      error="Organization is missing a url"
    )

  if createOrganizationRequest.location == None:
    return CreateOrganizationResponse(
      organizationUUID=None,
      organization=None,
      error="Organization is missing a location"
    )

  # Check if the location exists already, if not create a new location
  location = None
  locationRes = fetchLocationRepo(
    FetchLocationRequest = FetchLocationRequest(
      name=createOrganizationRequest.Location.name,
      street = createOrganizationRequest.Location.street,
      city = createOrganizationRequest.Location.city
    )
  )
  if locationRes.error != None:
    logger.info("Failed to fetch location at: " + str(createOrganizationRequest.Location.street) + ", " + str(createOrganizationRequest.Location.city))

    # Create new location
    createLocationRes = createLocationRepo(
      CreateLocationRequest = CreateLocationRequest(
        name=createOrganizationRequest.Location.name,
        street=createOrganizationRequest.Location.street,
        city=createOrganizationRequest.Location.city,
        state=createOrganizationRequest.Location.state,
        zip = createOrganizationRequest.Location.zip,
        country = createOrganizationRequest.Location.country,
      )
    )
    if createLocationRes.error != None:
      return CreateOrganizationResponse(
        organizationUUID=None,
        organization=None,
        error=createLocationRes.error
      )
    location = createLocationRes.Location

  else:
    location = locationRes.Location


  createOrganizationRes = createOrganizationRepo(
    CreateOrganizationRequest=CreateOrganizationRequest(
      name=createOrganizationRequest.name,
      description=createOrganizationRequest.description,
      image=createOrganizationRequest.image,
      backgroundImage=createOrganizationRequest.backgroundImage,
      location=location,
      url=createOrganizationRequest.url,
    )
  )

  if createOrganizationRes.error != None:
    return CreateOrganizationResponse(
      organizationUUID=None,
      organization=None,
      error= createOrganizationRes.error
    )

  else:
    return CreateOrganizationResponse


def generateRecommendedOrgsForNewsInfoCard(generateRecOrgsForNewsInfoCardRequest):
  """
    Generates recommended orgs for each news info card
  """
  pass




