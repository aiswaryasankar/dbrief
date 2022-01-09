from django.http.response import JsonResponse
from rest_framework.response import Response
import logging
from .repository import *
from .serializers import *
from logtail import LogtailHandler

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = []
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def hello_world(helloWorldRequest):
  """
    Demo function for testing purposes
  """
  logger.info(helloWorldRequest)
  logger.info(helloWorldRequest.name)
  return HelloWorldResponse(
    name=helloWorldRequest.name
  )


def create_newsletter_config_for_user(createNewsletterConfigRequest):
  """
    Create a newsletter config for a user
  """
  # Write the newsletter config settings in the newsletter config database


  # Write the user topics in the UserTopic database

  pass


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

  pass


def send_newsletters_batch(sendNewslettersBatchRequest):
  """
    Will query all the users that have subscribed to a newsletter at a given time of day/ day and call send_newsletter for each of them. Send_newsletters_batch_request will only take in the time of day and the day of week.  In the future this will need to account for time zones properly.
  """
  # Query the newsletter_config database for all the userIds that match the current time of day and day of week

  # Call send_newsletter for each of those userIds either in parallel or sequentially


  pass


def send_newsletter(sendNewsletterRequest):
  """
    Send a newsletter to a user
  """
  # Will take in a userId and query for the topics that the user follows

  # Will fetch the relevant information by passing the topic into getTopicPage

  # Will call hydrate_newsletter to populate the information into the newsletter template

  # Will handle sending out the email through mailchimp

  pass


def hydrate_newsletter(hydrateNewsletterRequest):
  """
    Hydrate the newsletter with the topic page results
  """
  # Will handle hydrating the newsletter given the information passed in through []TopicPage

  # Response type for this function is not yet known entirely

  pass




