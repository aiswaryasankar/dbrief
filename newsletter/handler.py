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
  for topic in newsletterConfig.TopicsFollowed:
    followTopicResponse = follow_topic(
      FollowTopicRequest(
        userId= newsletterConfig.UserID,
        topicId=topic,
        forNewsletter=True,
      )
    )
    if followTopicResponse.error != None:
      return CreateNewsletterConfigForUserResponse(
        newsletterId=None,
        error=followTopicResponse.error,
      )
    else:
      logger.info("Successfully followed topic")

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
  return GetNewsletterConfigForUserResponse(
    newsletterConfig=getNewsLetterConfigRes.res,
    error=None,
  )


def send_newsletters_batch(sendNewslettersBatchRequest):
  """
    Will query all the users that have subscribed to a newsletter at a given time of day/ day and call send_newsletter for each of them. Send_newsletters_batch_request will only take in the time of day and the day of week.  In the future this will need to account for time zones properly.
  """
  # Query the newsletter_config database for all the userIds that match the current time of day and day of week
  queryNewsletterConfigRes = queryNewsletterConfig(
    QueryNewsletterConfigRequest(
      deliveryTime=sendNewslettersBatchRequest.deliveryTime,
      day=sendNewslettersBatchRequest.day,
    )
  )
  if queryNewsletterConfigRes.error != None:
    return SendNewsletterResponse(
      error = queryNewsletterConfigRes.error
    )

  # Call send_newsletter for each of those userIds either in parallel or sequentially
  for config in queryNewsletterConfigRes.newsletterConfigs:
    sendNewsletterRes = send_newsletter(
      SendNewsletterRequest(
        userId= config.UserId,
      )
    )
    if sendNewsletterRes.error != None:
      return SendNewsletterResponse(
        error = sendNewsletterRes.error
      )



def send_newsletter(sendNewsletterRequest):
  """
    Send a newsletter to a user
  """
  # Get the user
  getUserRes = getUser(
    GetUserRequest(
      userId = sendNewsletterRequest.userId
    )
  )
  if getUserRes.error != None:
    return SendNewsletterResponse(
      error = getUserRes.error
    )

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

  # Will fetch the relevant information by passing the topic into getTopicPage
  for topic in newsletterTopicsRes.topics:
    fetchTopicPageRes = fetchTopicPage(
      FetchTopicPageRequest(
        topic=topic,
      )
    )
    if fetchTopicPageRes.error != None:
      return SendNewsletterResponse(
        error = fetchTopicPageRes.error
      )

  # Populate the template with the variables fetched through the topic page
  hydrateNewsletterRes = hydrate_newsletter(
    HydrateNewsletterRequest(

    )
  )

  # Send out the email
  message = Mail(
      from_email='from_email@example.com',
      to_emails='to@example.com',
      subject='Sending with Twilio SendGrid is Fun',
      html_content='<strong>and easy to do anywhere, even with Python</strong>')
  try:
      sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
      response = sg.send(message)
      print(response.status_code)
      print(response.body)
      print(response.headers)
  except Exception as e:
      print(e.message)


  # Will call hydrate_newsletter to populate the information into the newsletter template

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
  # Will handle hydrating the newsletter given the information passed in through []TopicPage

  # Response type for this function is not yet known entirely

  pass


