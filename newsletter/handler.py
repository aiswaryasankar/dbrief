from hashlib import new
from django.http.response import JsonResponse
from rest_framework.response import Response
import logging
from .repository import *
from .serializers import *
from userPreferences.handler import *
from topicFeed.handler import *
from logtail import LogtailHandler
import mailchimp_transactional as MailchimpTransactional
from mailchimp_transactional.api_client import ApiClientError
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sendgrid.helpers.mail import *


handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = []
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def create_newsletter_config_for_user(createNewsletterConfigRequest):
  """
    Create a newsletter config for a user
  """
  # Write the newsletter config settings in the newsletter config database
  createNewsletterConfigForUserResponse = updateNewsletterConfig(createNewsletterConfigRequest)
  if createNewsletterConfigForUserResponse.error != None:
    return createNewsletterConfigForUserResponse

  # Write the user topics in the UserTopic database
  newsletterConfig = createNewsletterConfigRequest.newsletterConfig

  # First fetch all the topics the user follows for the newsletter
  # If there are any topics that the user isn't currently including then remove those
  # Add any new topics
  # Current topics
  followingTopicsResponse = get_topics_you_follow(
    GetTopicsForUserRequest(
      user_id=newsletterConfig.UserID,
      for_newsletter=True,
    )
  )
  if followingTopicsResponse.error != None:
    return CreateNewsletterConfigForUserResponse(
      newsletterId=None,
      error=followingTopicsResponse.error,
    )

  topicsToFollow, topicsToUnfollow = [], []

  logger.info("Existing topics: " + str(followingTopicsResponse))
  logger.info("New topics: " + str(newsletterConfig.TopicsFollowed))

  for topic in newsletterConfig.TopicsFollowed:
    if topic not in followingTopicsResponse.topics:
      topicsToFollow.append(topic)

  for topic in followingTopicsResponse.topics:
    if topic not in newsletterConfig.TopicsFollowed:
      topicsToUnfollow.append(topic)

  logger.info("Topics to follow: " + str(topicsToFollow))
  logger.info("Topics to unfollow: " + str(topicsToUnfollow))

  for topic in topicsToFollow:
      # Topic needs to be added
      followTopicResponse = follow_topic(
        FollowTopicRequest(
          userId= newsletterConfig.UserID,
          topicId=topic.TopicID,
          forNewsletter=True,
        )
      )
      if followTopicResponse.error != None:
        return CreateNewsletterConfigForUserResponse(
          newsletterId=None,
          error=followTopicResponse.error,
        )
      else:
        logger.info("Successfully followed topic: " + str(topic.TopicID))

  for topic in topicsToUnfollow:
      # Topic needs to be added
      unfollowTopicResponse = unfollow_topic(
        UnfollowTopicRequest(
          userId= newsletterConfig.UserID,
          topicId=topic.TopicID,
        )
      )
      if unfollowTopicResponse.error != None:
        return CreateNewsletterConfigForUserResponse(
          newsletterId=None,
          error=unfollowTopicResponse.error,
        )
      else:
        logger.info("Successfully unfollowed topic: " + str(topic.TopicID))

  return createNewsletterConfigForUserResponse


def update_newsletter_config_for_user(updateNewsletterConfigRequest):
  """
    Update existing newsletter for a user
  """
  # Call the repo function with update_or_create using the newsletterConfigId

  pass


def get_newsletter_config_for_user(getNewsletterConfigRequest):
  """
    Get already created newsletter for a user
  """
  # Basic retrieval on the newsletter config based on userId
  getNewsLetterConfigRes = getNewsletterConfig(getNewsletterConfigRequest)
  if getNewsLetterConfigRes.error != None:
    return GetNewsletterConfigForUserResponse(
      newsletterConfig=None,
      error=getNewsLetterConfigRes.error
    )

  # Hydrate the topics that a user is following
  getTopicsYouFollowResponse = get_topics_you_follow(
    getTopicsYouFollowRequest=GetTopicsForUserRequest(
      user_id=getNewsletterConfigRequest.userId,
      for_newsletter=True,
    )
  )
  logger.info("topics you follow")
  logger.info(getTopicsYouFollowResponse.topics)
  if getTopicsYouFollowResponse.error != None:
    return GetNewsletterConfigForUserResponse(
      newsletterConfig=None,
      error=getTopicsYouFollowResponse.error
    )

  getNewsLetterConfigRes.newsletterConfig.TopicsFollowed = getTopicsYouFollowResponse.topics

  logger.info("getNewsletterConfigRes")
  logger.info(getNewsLetterConfigRes.newsletterConfig.TopicsFollowed)

  return GetNewsletterConfigForUserResponse(
    newsletterConfig=getNewsLetterConfigRes.newsletterConfig,
    error=None,
  )


def send_newsletters_batch(sendNewslettersBatchRequest):
  """
    Will query all the users that have subscribed to a newsletter at a given time of day/ day and call send_newsletter for each of them. Send_newsletters_batch_request will only take in the time of day and the day of week.  In the future this will need to account for time zones properly.
  """
  # Query the newsletter_config database for all the userIds that match the current time of day and day of week
  queryNewsletterConfigRes = queryNewsletterConfig(
    QueryNewsletterConfigRequest(
      deliveryTime=sendNewslettersBatchRequest.timeOfDay,
      day=sendNewslettersBatchRequest.day,
    )
  )
  if queryNewsletterConfigRes.error != None:
    logger.info("QUERY ERR")
    return SendNewsletterResponse(
      error = queryNewsletterConfigRes.error
    )

  # Call send_newsletter for each of those userIds either in parallel or sequentially
  for config in queryNewsletterConfigRes.newsletterConfigs:
    sendNewsletterRes = send_newsletter(
      SendNewsletterRequest(
        userId= config.userId,
      )
    )
    logger.info("SUCCESSFULLY SENT NEWSLETTER")
    if sendNewsletterRes.error != None:
      return SendNewsletterResponse(
        error = sendNewsletterRes.error
      )

  return SendNewsletterResponse(
    error=None
  )


def send_newsletter(sendNewsletterRequest):
  """
    Send a newsletter to a user
  """
  # Get the user

  getUserRes = get_user(
    GetUserRequest(
      userId = sendNewsletterRequest.userId
    )
  )
  if getUserRes.error != None:
    logger.info("FAILED TO GET USER")
    return SendNewsletterResponse(
      error = getUserRes.error
    )

  logger.info("USER")
  logger.info(getUserRes)

  # Will take in a userId and query for the topics that the user follows
  newsletterTopicsRes = get_topics_you_follow(
    GetTopicsForUserRequest(
      user_id=sendNewsletterRequest.userId,
      for_newsletter=True,
    )
  )
  if newsletterTopicsRes.error != None or len(newsletterTopicsRes.topics) == 0:
    logger.warn("No topics for user")
    return SendNewsletterResponse(
      error = newsletterTopicsRes.error
    )

  logger.info("TOPICS FOLLOWED")
  logger.info(newsletterTopicsRes)

  # Will fetch the relevant information by passing the topic into getTopicPage
  topicPages = []
  for topic in newsletterTopicsRes.topics:
    fetchTopicPageRes = getTopicPage(
      GetTopicPageRequest(
        topicName=topic.TopicName,
      )
    )
    if fetchTopicPageRes.error != None:
      continue
    else:
      topicPages.append(fetchTopicPageRes.topic_page)

  logger.info("TOPIC PAGES")
  logger.info(topicPages)

  # Populate the template with the variables fetched through the topic page
  hydrateNewsletterRes = hydrate_newsletter(
    HydrateNewsletterRequest(
      topicPages=topicPages,
    )
  )
  if hydrateNewsletterRes.error != None:
    return SendNewsletterResponse(
      error = hydrateNewsletterRes.error
    )
  logger.info(hydrateNewsletterRes)

  # Send out the email
  # template_id = "d-e59e28f3ae8543ccb4f67f59eb418d39"
  template_id = "d-52147667a88c45e6a0eb33ccb83adae4"

  sg = SendGridAPIClient('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')

  message = Mail()
  toEmail = getUserRes.User.Email
  recipientName = getUserRes.User.FirstName + " " + getUserRes.User.LastName

  message.to = [
    To(
        email=toEmail,
        name=recipientName,
        p=0
    )
  ]
  message.from_email = From(
    email="aiswarya.s@berkeley.edu",
    name="Dbrief.AI",
    p=1
  )
  message.subject = Subject("Dbrief.AI")

  message.tracking_settings = TrackingSettings(
    click_tracking=ClickTracking(
        enable=True,
        enable_text=False
    ),
    open_tracking=OpenTracking(
        enable=True,
        substitution_tag=OpenTrackingSubstitutionTag("%open-track%")
    ),
    subscription_tracking=SubscriptionTracking(False)
  )

  message.template_id = template_id

  hydrateNewsletterRes = hydrate_newsletter(
    HydrateNewsletterRequest(
      topicPages=topicPages,
    )
  )
  if hydrateNewsletterRes.error != None:
    return SendNewsletterResponse(
      error=hydrateNewsletterRes.error
    )

  message.dynamic_template_data = hydrateNewsletterRes.newsletter

  try:
      response = sg.send(message)
      print(response.status_code)
      print(response.body)
      print(response.headers)
  except Exception as e:
      print(e)

  return SendNewsletterResponse(
    error=None
  )


def send_newsletter_mailchimp():
  """
    Deprecated endpoint supporting emails through mailchimp
  """

  mailchimp = MailchimpTransactional.Client('IbRJVT9R9C9JBt6gUA-E3g')
  message = {
      "from_email": "aiswarya.s@dbrief.ai",
      "subject": "Hello world",
      "text": "Demo email!",
      "to": [
        {
          "email": "aiswarya.s@dbrief.ai",
          "type": "to"
        }
      ]
  }

  try:
    response = mailchimp.messages.send({"message":message})
    print('API called successfully: {}'.format(response))
  except ApiClientError as error:
    print('An exception occurred: {}'.format(error.text))


def hydrate_newsletter(hydrateNewsletterRequest):
  """
    Hydrate the newsletter with the topic page results
  """
  topicPages = hydrateNewsletterRequest.topicPages

  # Will handle hydrating the newsletter given the information passed in through []TopicPage
  if len(topicPages) > 0:
    newsletter = {
      "Topic_Name": topicPages[0].TopicName,
      "Story_Title": topicPages[0].Title,
      "Story_Content": topicPages[0].MDSSummary[2:],
      "Picture": topicPages[0].ImageURL,
      "Fact_Content1": topicPages[0].Facts[0].Quote.Text,
      "Fact_Author1": topicPages[0].Facts[0].Quote.Author[2:-2],
      "Fact_Link1": topicPages[0].Facts[0].Quote.SourceURL,
      "Fact_Content2": topicPages[0].Facts[1].Quote.Text,
      "Fact_Author2": topicPages[0].Facts[1].Quote.Author[2:-2],
      "Fact_Link2": topicPages[0].Facts[1].Quote.SourceURL,
      "View_Type1": "Left Leaning",
      "Opinion_Content1": topicPages[0].Opinions[0].Quote.Text,
      "Opinion_Author1": topicPages[0].Opinions[0].Quote.Author[2:-2],
      "Opinion_Link1": topicPages[0].Opinions[0].Quote.SourceURL,
      "View_Type2": "Right Leaning",
      "Opinion_Content2": topicPages[0].Opinions[1].Quote.Text,
      "Opinion_Author2": topicPages[0].Opinions[1].Quote.Author[2:-2],
      "Opinion_Link2": topicPages[0].Opinions[1].Quote.SourceURL,
    }
  else:
    return HydrateNewsletterResponse(
      newsletter=None,
      error="No topic pages to hydrate"
    )

  logger.info("NEWSLETTER")
  logger.info(json.dumps(newsletter))

  # Returns the populated variables
  return HydrateNewsletterResponse(
    newsletter=newsletter,
    error=None,
  )

