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

  elif generateRecOrgsForNewsInfoCardRequest.newsInfoCard != None:
    newsInfoCard = generateRecOrgsForNewsInfoCardRequest.newsInfoCard

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

  # Rank the returned list
  allOrgsRes = fetchAllOrganizationsRepo(
    FetchOrgnizationsRequest(
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
  embeddingModel = hub.load(module)
  descriptions = [org.description for org in rankOrganizationsForNewsInfoCardRequest.orgList]
  descriptionEmbed = [embeddingModel([description]) for description in descriptions]

  # Compute the similarity with the given newsInfoCard summary
  summaryEmbed = [embeddingModel([rankOrganizationsForNewsInfoCardRequest.newsInfoCard.summary])]
  summaryEmbedMatrix = [summaryEmbed for i in range(len(descriptionEmbed))]


  # Create a matrix of facts and compute the dot product between the matrices
  dot_products = np.dot(descriptionEmbed, summaryEmbedMatrix.T)

  # Return the top row as the result
  dot_product_sum = sum(dot_products)
  if len(dot_product_sum) >= 3:
    top_org_indices = np.argpartition(dot_product_sum, -len(descriptions))[-len(descriptions):]
  else:
    top_org_indices = [i for i in range(len(dot_product_sum))]

  # Top orgs
  top_orgs = [rankOrganizationsForNewsInfoCardRequest.orgList[index] for index in top_org_indices]

  # Return the ranked list by similarity
  return RankOrganizationsForNewsInfoCardResponse(
    rankedOrganizations=[RankedOrganization(
      organization=top_orgs[i],
      rank=i)
      for i in range(len(top_orgs))
    ],
    error=None,
  )




