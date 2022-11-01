"""
  This service is primarily responsible for creating new organizations.
"""

import logging
from articleRec import handler as articleRecHandler
from mdsModel import handler as mdsHandler
from polarityModel.handler import *
from topicFeed import handler as topicFeedHandler
from .repository import *
from topicModeling import handler as tpHandler
from newsInfoCard.handler import *
from organizations.handler import *
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
    FetchLocationRequest(
      name=createOrganizationRequest.location.name,
      street = createOrganizationRequest.location.street,
      city = createOrganizationRequest.location.city
    )
  )
  if locationRes.error != None:
    logger.info("Failed to fetch location at: " + str(createOrganizationRequest.location.street) + ", " + str(createOrganizationRequest.location.city))

    # Create new location
    createLocationRes = createLocationRepo(
      CreateLocationRequest(
        name=createOrganizationRequest.location.name,
        street=createOrganizationRequest.location.street,
        city=createOrganizationRequest.location.city,
        state=createOrganizationRequest.location.state,
        zip = createOrganizationRequest.location.zip,
        country = createOrganizationRequest.location.country,
      )
    )
    if createLocationRes.error != None:
      return CreateOrganizationResponse(
        organizationUUID=None,
        organization=None,
        error=createLocationRes.error
      )
    location = createLocationRes.location

  else:
    location = locationRes.location


  createOrganizationRes = createOrganizationRepo(
    CreateOrganizationRepoRequest(
      name=createOrganizationRequest.name,
      description=createOrganizationRequest.description,
      image=createOrganizationRequest.image,
      backgroundImage=createOrganizationRequest.backgroundImage,
      locationUUID=location.uuid,
      url=createOrganizationRequest.url,
      email=createOrganizationRequest.email,
    )
  )

  if createOrganizationRes.error != None:
    return CreateOrganizationResponse(
      organizationUUID=None,
      organization=None,
      error= createOrganizationRes.error
    )

  # Create the causes associated with the organization
  for cause in createOrganizationRequest.causes:
    createCauseRes = createCausesForOrganizationsRepo(
      CreateCausesForOrganizationRepoRequest(
        organizationUUID=createOrganizationRes.organizationUUID,
        cause= cause
      )
    )
    if createCauseRes.error != None:
      logger.warn("Failed to set cause for organization")

  return createOrganizationRes


def generateRecommendedOrgsForNewsInfoCard(generateRecOrgsForNewsInfoCardRequest):
  """
    Generates recommended orgs for each news info card
  """
  newsInfoCard = None

  if generateRecOrgsForNewsInfoCardRequest.newsInfoCardUUID != None:
    # Fetch the news info card with UUID
    fetchNewsInfoCardRes = fetchNewsInfoCard(
      FetchNewsInfoCardRequest(
        newsInfoCardUUID=generateRecOrgsForNewsInfoCardRequest.newsInfoCardUUID
      )
    )
    if fetchNewsInfoCardRes.error != None:
      return GenerateRecommendedOrgsForNewsInfoCardResponse(
        orgList=None,
        error=fetchNewsInfoCardRes.error
      )
    newsInfoCard = fetchNewsInfoCardRes.newsInfoCard

  elif generateRecOrgsForNewsInfoCardRequest.newsInfoCard != None:
    newsInfoCard = generateRecOrgsForNewsInfoCardRequest.newsInfoCard

  print(newsInfoCard)

  # Get the top3 document causes
  getDocumentCausesResponse = get_document_cause(
    GetDocumentCauseRequest(
      query=newsInfoCard.summary
    )
  )
  if getDocumentCausesResponse.error != None:
    return GenerateRecommendedOrgsForNewsInfoCardResponse(
      orgList=None,
      error=getDocumentCausesResponse.error
    )

  # Filter organizations based on the causes
  causes = getDocumentCausesResponse.causeList
  logger.info("Most relevant causes for newsInfoCard: " + str(causes))

  # Rank the returned list
  allOrgsRes = fetchOrganizationsRepo(
    FetchOrgnizationsRequest(
      uuids=[],
      causes=causes,
    )
  )
  if allOrgsRes.error != None:
    return GenerateRecommendedOrgsForNewsInfoCardResponse(
      orgList=None,
      error=allOrgsRes.error,
    )
  logger.info("Fetched %s organizations for newsInfoCard", len(allOrgsRes.orgList))

  # Rank the article against all the organizations
  rankedOrganizationsRes = rankOrganizationsForNewsInfoCard(
    rankOrganizationsForNewsInfoCardRequest=RankOrganizationsForNewsInfoCardRequest(
      orgList=allOrgsRes.orgList,
      newsInfoCard=newsInfoCard,
    )
  )
  if rankedOrganizationsRes.error != None:
    return GenerateRecommendedOrgsForNewsInfoCardResponse(
      orgList=None,
      error=rankedOrganizationsRes.error
    )

  # Store the recommendations in the recommendedOrganizationsForNewsInfoCard service
  for rankedOrg in rankedOrganizationsRes.rankedOrganizations:
    createRecommendedOrgsForNewsInfoCardRes = createRecommendedOrgsForNewsInfoCardRepo(
      CreateRecommendedOrgsForNewsInfoCardRepoRequest(
        newsInfoCardUUID=generateRecOrgsForNewsInfoCardRequest.newsInfoCardUUID,
        organizationUUID=rankedOrg.organization.uuid,
        rank=rankedOrg.rank
      )
    )
    if createRecommendedOrgsForNewsInfoCardRes.error != None:
      return GenerateRecommendedOrgsForNewsInfoCardResponse(
        orgList=None,
        error=createRecommendedOrgsForNewsInfoCardRes.error
      )

  return GenerateRecommendedOrgsForNewsInfoCardResponse(
    orgList=rankedOrganizationsRes.rankedOrganizations,
    error=createRecommendedOrgsForNewsInfoCardRes.error
  )


def getRecommendedOrgsForNewsInfoCard(getRecommendedOrgsForNewsInfoCardRequest):
  """
    Returns a list of the recommended orgs for each news info card
  """
  pass


def rankOrganizationsForNewsInfoCard(rankOrganizationsForNewsInfoCardRequest):
  """
    Ranks organizations for each news info card
  """

  # Pull the description for each of the organizations
  orgList = rankOrganizationsForNewsInfoCardRequest.orgList
  logger.info("Number of orgs to rank: " + str(len(orgList)))

  embeddingModel = hub.load(module)
  descriptions = [org.description for org in orgList]
  descriptionEmbed = [embeddingModel([description]) for description in descriptions]
  logger.info("Description embedding: " + str(descriptionEmbed))

  # Compute the similarity with the given newsInfoCard summary
  summaryEmbed = [embeddingModel([rankOrganizationsForNewsInfoCardRequest.newsInfoCard.summary])]
  summaryEmbedMatrix = [summaryEmbed for i in range(len(descriptionEmbed))]
  summaryEmbedMatrix = np.squeeze(summaryEmbedMatrix)
  logger.info("Summary embedding: " + str(summaryEmbedMatrix))

  # Create a matrix of facts and compute the dot product between the matrices
  dot_products = np.dot(descriptionEmbed, summaryEmbedMatrix.T)

  # Return the top row as the result
  dot_product_sum = sum(dot_products)
  if len(dot_product_sum) >= 10:
    top_org_indices = np.argpartition(dot_product_sum, -10)[-10:]
  else:
    top_org_indices = [i for i in range(len(dot_product_sum))]
  logger.info("Top_org_indices: " + str(top_org_indices))

  # Top orgs
  top_orgs = [orgList[index] for index in top_org_indices]
  logger.info("Top orgs: " + str(top_orgs))

  # Return the ranked list by similarity
  return RankOrganizationsForNewsInfoCardResponse(
    rankedOrganizations=[RankedOrganization(
      organization=top_orgs[i],
      rank=i)
      for i in range(len(top_orgs))
    ],
    error=None,
  )


