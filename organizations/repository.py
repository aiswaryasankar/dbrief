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

    return CreateLocationResponse(uuid=None, location=None, error=e)

  return CreateLocationResponse(uuid=location.uuid, location=location, error=None)


def fetchLocationRepo(fetchLocationRequest):
  """
    Will fetch a location from the db given unique key of street
  """
  street = fetchLocationRequest.street
  city = fetchLocationRequest.city

  try:
    locationRes = LocationModel.objects.get(street=street, city=city)

  except Exception as e:
    logger.warn("Failed to fetch location with street: " + str(street) + " " + str(city)  + " error: " + str(e))

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
      name = createOrganizationRequest.name,
      defaults={
        'uuid': organizationUUID,
        'description': createOrganizationRequest.description,
        'image': createOrganizationRequest.image,
        'backgroundImage': createOrganizationRequest.backgroundImage,
        'locationUUID': createOrganizationRequest.locationUUID,
        'url': createOrganizationRequest.url,
        'email': createOrganizationRequest.email,
      },
    )
    if created:
      logger.info('Saved organization')

  except Exception as e:
    logger.warn("Failed to save organization to the database: " + str(e))

    return CreateOrganizationResponse(organizationUUID=None, organization=None, error=e)

  return CreateOrganizationResponse(organizationUUID=org.uuid, organization=org, error=None)


def fetchOrganizationsRepo(fetchOrganizationsRequest):
  """
    Fetch an organization given UUID or a list of causes
  """
  orgList = []

  if fetchOrganizationsRequest.uuids != []:
    try:
      organizationRes = OrganizationModel.objects.get(uuid=fetchOrganizationsRequest.uuid)
      org = Organization(
          uuid=organization.uuid,
          name=organization.name,
          description=organization.description,
          link=organization.url,
          image=organization.image,
          backgroundImage= organization.backgroundImage,
          locationUUID=organization.locationUUID,
        )
      orgList.append(org)

    except Exception as e:
      logger.warn("Failed to fetch organization with uuid: " + str(uuid)  + " error: " + str(e))

  elif fetchOrganizationsRequest.causes != []:
    logger.info("Fetching organizations for causes: " + str(fetchOrganizationsRequest.causes))

    try:
      # Fetch all orgUUIDs that have a cause in the cause list
      causesRes = OrganizationCausesModel.objects.filter(cause__in=fetchOrganizationsRequest.causes)

      # Fetch orgs corresponding to the UUIDs
      for org in causesRes:
        try:
          organization = OrganizationModel.objects.get(uuid=org.organizationUUID)
          org = Organization(
            uuid=organization.uuid,
            name=organization.name,
            description=organization.description,
            link=organization.url,
            image=organization.image,
            backgroundImage= organization.backgroundImage,
            locationUUID=organization.locationUUID,
          )
          orgList.append(org)
          logger.info("Fetched %s orgs matching given causes", len(causesRes))

        except Exception as e:
          logger.warn("Failed to fetch organizations with uuid: " + str(org.uuid)  + " error: " + str(e))

    except Exception as e:
      logger.warn("Failed to fetch causes for organization with cause: " + str(fetchOrganizationsRequest.causes)  + " error: " + str(e))

  return FetchAllOrganizationsResponse(
    orgList=orgList,
    error=None,
  )


def fetchAllOrganizationsRepo(fetchAllOrganizationsRequest):
  """
    Returns a hydrated list of all organizations
  """
  allOrgs = []

  for organization in OrganizationModel.objects.all():
    try:
      org = Organization(
          uuid=organization.uuid,
          name=organization.name,
          description=organization.description,
          link=organization.url,
          image=organization.image,
          backgroundImage= organization.backgroundImage,
          locationUUID=organization.locationUUID,
        )

      allOrgs.append(org)

    except Exception as e:
      logger.warn("Failed to fetch organization from database")
      print(e)

  return FetchAllOrganizationsResponse(
    orgList=allOrgs,
    error=None,
  )


def createRecommendedOrgsForNewsInfoCardRepo(recommendedOrgsForNewsInfoCardRequest):
  """
    Stores the recommended orgs for each news info card
  """
  recUuid = str(uuid.uuid1())
  try:
    _, created = RecommendedOrgsForNewsInfoCardModel.objects.update_or_create(
      uuid = recUuid,
      defaults={
        'newsInfoCardUUID': recommendedOrgsForNewsInfoCardRequest.newsInfoCardUUID,
        'organizationUUID': recommendedOrgsForNewsInfoCardRequest.organizationUUID,
        'rank': recommendedOrgsForNewsInfoCardRequest.rank,
      },
    )
    if created:
      logger.info('Saved org recommendation')

  except Exception as e:
    logger.warn("Failed to save recommendation to the database: " + str(e))

    return CreateRecommendedOrgsForNewsInfoCardRepoResponse(error=e)

  return CreateRecommendedOrgsForNewsInfoCardRepoResponse(error=None)


def createCausesForOrganizationsRepo(createCausesForOrganizationRepoRequest):
  """
    Set the causes associated with the organization.
  """

  causeUuid = str(uuid.uuid1())
  try:
    _, created = OrganizationCausesModel.objects.update_or_create(
      uuid = causeUuid,
      defaults={
        'organizationUUID': createCausesForOrganizationRepoRequest.organizationUUID,
        'cause': createCausesForOrganizationRepoRequest.cause,
      },
    )
    if created:
      logger.info('Saved cause for org')

  except Exception as e:
    logger.warn("Failed to save cause for org to the database: " + str(e))

    return CreateCausesForOrganizationRepoResponse(error=e)

  return CreateCausesForOrganizationRepoResponse(error=None)




