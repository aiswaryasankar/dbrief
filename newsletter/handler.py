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
  logger.info("STARTING")
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

  logger.info("CALLING SEND NEWSLETTER")
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
  logger.info("CALLING GET USER")
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
    fetchTopicPageRes = fetchTopicPage(
      FetchTopicPageRequest(
        topic="",
        topicPageId=topic.TopicID,
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

  logger.info("HYDRATED DATA")
  logger.info(hydrateNewsletterRes)

  # Send out the email
  logger.info("GETTING READY TO SEND OUT")
  template_id = ["d-dbf2e565bcbe45919a98a38834adbbe3"]

  logger.info("SENDGRID KEYYYYYYYYYYYYYYY")
  sg = SendGridAPIClient('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')
  # response = sg.client.templates._(template_id).post(
  #   request_body=hydrateNewsletterRes.newsletter
  # )

  message = Mail()
  message.to = [
    To(
        email="aiswarya.s@berkeley.edu",
        name="Aiswarya Sankar",
        p=0
    )
  ]
  message.from_email = From(
    email="aiswarya.s@berkeley.edu",
    name="Example Sales Team",
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

  message.content = [
      Content(
          mime_type="text/html",
          content="""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html data-editor-version="2" class="sg-campaigns" xmlns="http://www.w3.org/1999/xhtml">
    <head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1, maximum-scale=1">
      <!--[if !mso]><!-->
      <meta http-equiv="X-UA-Compatible" content="IE=Edge">
      <!--<![endif]-->
      <!--[if (gte mso 9)|(IE)]>
      <xml>
        <o:OfficeDocumentSettings>
          <o:AllowPNG/>
          <o:PixelsPerInch>96</o:PixelsPerInch>
        </o:OfficeDocumentSettings>
      </xml>
      <![endif]-->
      <!--[if (gte mso 9)|(IE)]>
  <style type="text/css">
    body {width: 600px;margin: 0 auto;}
    table {border-collapse: collapse;}
    table, td {mso-table-lspace: 0pt;mso-table-rspace: 0pt;}
    img {-ms-interpolation-mode: bicubic;}
  </style>
<![endif]-->
      <style type="text/css">
    body, p, div {
      font-family: inherit;
      font-size: 14px;
    }
    body {
      color: #000000;
    }
    body a {
      color: #272525;
      text-decoration: none;
    }
    p { margin: 0; padding: 0; }
    table.wrapper {
      width:100% !important;
      table-layout: fixed;
      -webkit-font-smoothing: antialiased;
      -webkit-text-size-adjust: 100%;
      -moz-text-size-adjust: 100%;
      -ms-text-size-adjust: 100%;
    }
    img.max-width {
      max-width: 100% !important;
    }
    .column.of-2 {
      width: 50%;
    }
    .column.of-3 {
      width: 33.333%;
    }
    .column.of-4 {
      width: 25%;
    }
    ul ul ul ul  {
      list-style-type: disc !important;
    }
    ol ol {
      list-style-type: lower-roman !important;
    }
    ol ol ol {
      list-style-type: lower-latin !important;
    }
    ol ol ol ol {
      list-style-type: decimal !important;
    }
    @media screen and (max-width:480px) {
      .preheader .rightColumnContent,
      .footer .rightColumnContent {
        text-align: left !important;
      }
      .preheader .rightColumnContent div,
      .preheader .rightColumnContent span,
      .footer .rightColumnContent div,
      .footer .rightColumnContent span {
        text-align: left !important;
      }
      .preheader .rightColumnContent,
      .preheader .leftColumnContent {
        font-size: 80% !important;
        padding: 5px 0;
      }
      table.wrapper-mobile {
        width: 100% !important;
        table-layout: fixed;
      }
      img.max-width {
        height: auto !important;
        max-width: 100% !important;
      }
      a.bulletproof-button {
        display: block !important;
        width: auto !important;
        font-size: 80%;
        padding-left: 0 !important;
        padding-right: 0 !important;
      }
      .columns {
        width: 100% !important;
      }
      .column {
        display: block !important;
        width: 100% !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
      }
      .social-icon-column {
        display: inline-block !important;
      }
    }
  </style>
    <style>
      @media screen and (max-width:480px) {
        table\0 {
          width: 480px !important;
          }
      }
    </style>
      <!--user entered Head Start--><link href="https://fonts.googleapis.com/css?family=Chivo&display=swap" rel="stylesheet"><style>
body {font-family: 'Chivo', sans-serif;}
</style><!--End Head user entered-->
    </head>
    <body>
      <center class="wrapper" data-link-color="#272525" data-body-style="font-size:14px; font-family:inherit; color:#000000; background-color:#000000;">
        <div class="webkit">
          <table cellpadding="0" cellspacing="0" border="0" width="100%" class="wrapper" bgcolor="#000000">
            <tr>
              <td valign="top" bgcolor="#000000" width="100%">
                <table width="100%" role="content-container" class="outer" align="center" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td width="100%">
                      <table width="100%" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                          <td>
                            <!--[if mso]>
    <center>
    <table><tr><td width="600">
  <![endif]-->
                                    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%; max-width:600px;" align="center">
                                      <tr>
                                        <td role="modules-container" style="padding:0px 0px 0px 0px; color:#000000; text-align:left;" bgcolor="#F4F4F4" width="100%" align="left"><table class="module preheader preheader-hide" role="module" data-type="preheader" border="0" cellpadding="0" cellspacing="0" width="100%" style="display: none !important; mso-hide: all; visibility: hidden; opacity: 0; color: transparent; height: 0; width: 0;">
    <tr>
      <td role="module-content">
        <p></p>
      </td>
    </tr>
  </table><table class="wrapper" role="module" data-type="image" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="08374cac-039d-45b1-a232-c0e5089212ae">
    <tbody>
      <tr>
        <td style="font-size:6px; line-height:10px; padding:0px 0px 0px 0px;" valign="top" align="left">
          <img class="max-width" border="0" style="display:block; color:#000000; text-decoration:none; font-family:Helvetica, arial, sans-serif; font-size:16px;" width="200" alt="" data-proportionally-constrained="true" data-responsive="false" src="http://cdn.mcauto-images-production.sendgrid.net/dfefe54e0a719529/615f8f88-12f4-414d-aca0-54acfad5748e/364x115.png" height="63">
        </td>
      </tr>
    </tbody>
  </table><table border="0" cellpadding="0" cellspacing="0" align="center" width="100%" role="module" data-type="columns" style="padding:0px 30px 0px 30px;" bgcolor="#f4f4f4" data-distribution="1">
    <tbody>
      <tr role="module-content">
        <td height="100%" valign="top"><table width="540" style="width:540px; border-spacing:0; border-collapse:collapse; margin:0px 0px 0px 0px;" cellpadding="0" cellspacing="0" align="left" border="0" bgcolor="" class="column column-0">
      <tbody>
        <tr>
          <td style="padding:0px;margin:0px;border-spacing:0;"><table class="module" role="module" data-type="text" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="5a6041a6-73be-403f-a78b-617bee55456a.1" data-mc-module-version="2019-10-22">
    <tbody>
      <tr>
        <td style="padding:0px 0px 0px 0px; line-height:40px; text-align:inherit;" height="100%" valign="top" bgcolor="" role="module-content"><div><div style="font-family: inherit; text-align: start"><span style="color: #908888"><strong>Vaccinate</strong></span></div><div></div></div></td>
      </tr>
    </tbody>
  </table><table class="module" role="module" data-type="text" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="e4965f1a-899b-4ab9-b1ff-490f07ea00a0.2" data-mc-module-version="2019-10-22">
    <tbody>
      <tr>
        <td style="padding:0px 40px 3px 0px; line-height:22px; text-align:inherit;" height="100%" valign="top" bgcolor="" role="module-content"><div><div style="font-family: inherit; text-align: inherit"><span style="font-size: 24px"><strong>Here's how the doses of the two vaccines for young children differ.</strong></span></div><div></div></div></td>
      </tr>
    </tbody>
  </table></td>
        </tr>
      </tbody>
    </table></td>
      </tr>
    </tbody>
  </table><table border="0" cellpadding="0" cellspacing="0" align="center" width="100%" role="module" data-type="columns" style="padding:0px 5px 0px 30px;" bgcolor="#f4f4f4" data-distribution="1,1">
    <tbody>
      <tr role="module-content">
        <td height="100%" valign="top"><table width="282" style="width:282px; border-spacing:0; border-collapse:collapse; margin:0px 0px 0px 0px;" cellpadding="0" cellspacing="0" align="left" border="0" bgcolor="" class="column column-0">
      <tbody>
        <tr>
          <td style="padding:0px;margin:0px;border-spacing:0;"><table class="module" role="module" data-type="text" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="e4965f1a-899b-4ab9-b1ff-490f07ea00a0.3" data-mc-module-version="2019-10-22">
    <tbody>
      <tr>
        <td style="padding:18px 40px 18px 0px; line-height:18px; text-align:inherit;" height="100%" valign="top" bgcolor="" role="module-content"><div><div style="font-family: inherit; text-align: left"><span style="font-size: 12px; font-family: inherit">Vaccines from Pfizer and its partner BioNTech have already been available for Americans 6 and older, and Moderna's vaccines for adults. For the first time since the pandemic began, almost every American, barring infants younger than 6 months, can be vaccinated against Covid. But as the earliest shots for the 19 million US children under age 5 roll out, researchers and frontline experts worry that the newly authorized vaccines will face both logistical challenges and a lack of public enthusiasm --- leaving kids vulnerable to the virus</span></div><div></div></div></td>
      </tr>
    </tbody>
  </table></td>
        </tr>
      </tbody>
    </table><table width="282" style="width:282px; border-spacing:0; border-collapse:collapse; margin:0px 0px 0px 0px;" cellpadding="0" cellspacing="0" align="left" border="0" bgcolor="" class="column column-1">
      <tbody>
        <tr>
          <td style="padding:0px;margin:0px;border-spacing:0;"><table class="wrapper" role="module" data-type="image" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="fb763f48-7056-4982-b560-d921e12efe42">
    <tbody>
      <tr>
        <td style="font-size:6px; line-height:10px; padding:50px 0px 35px 0px;" valign="top" align="right"><img class="max-width" border="0" "border-radius:="" 30px;"="" style="display:block; color:#000000; text-decoration:none; font-family:Helvetica, arial, sans-serif; font-size:16px;" width="275" alt="" data-proportionally-constrained="true" data-responsive="false" src="http://cdn.mcauto-images-production.sendgrid.net/dfefe54e0a719529/d87e2841-4cc0-4c6d-a110-3bb541fc574f/1100x619.jpg" height="155"></td>
      </tr>
    </tbody>
  </table></td>
        </tr>
      </tbody>
    </table></td>
      </tr>
    </tbody>
  </table><table border="0" cellpadding="0" cellspacing="0" align="center" width="100%" role="module" data-type="columns" style="padding:2px 270px 0px 30px;" bgcolor="#f4f4f4" data-distribution="1,1">
    <tbody>
      <tr role="module-content">
        <td height="100%" valign="top"><table width="150" style="width:150px; border-spacing:0; border-collapse:collapse; margin:0px 0px 0px 0px;" cellpadding="0" cellspacing="0" align="left" border="0" bgcolor="" class="column column-0">
      <tbody>
        <tr>
          <td style="padding:0px;margin:0px;border-spacing:0;"><table border="0" cellpadding="0" cellspacing="0" class="module" data-role="module-button" data-type="button" role="module" style="table-layout:fixed;" width="100%" data-muid="f1532651-662d-4412-8192-0bbe0e837a35.1.1">
      <tbody>
        <tr>
          <td align="left" bgcolor="" class="outer-td" style="padding:0px 0px 0px 0px;">
            <table border="0" cellpadding="0" cellspacing="0" class="wrapper-mobile" style="text-align:center;">
              <tbody>
                <tr>
                <td align="center" bgcolor="#f88524" class="inner-td" style="border-radius:6px; font-size:16px; text-align:left; background-color:inherit;">
                  <a href="" style="background-color:#f88524; border:1px solid #ed8d15; border-color:#ed8d15; border-radius:8px; border-width:1px; color:#ffffff; display:inline-block; font-size:14px; font-weight:normal; letter-spacing:0px; line-height:normal; padding:8px 45px 8px 45px; text-align:center; text-decoration:none; border-style:solid; font-family:arial black, helvetica, sans-serif;" target="_blank">Follow</a>
                </td>
                </tr>
              </tbody>
            </table>
          </td>
        </tr>
      </tbody>
    </table></td>
        </tr>
      </tbody>
    </table><table width="150" style="width:150px; border-spacing:0; border-collapse:collapse; margin:0px 0px 0px 0px;" cellpadding="0" cellspacing="0" align="left" border="0" bgcolor="" class="column column-1">
      <tbody>
        <tr>
          <td style="padding:0px;margin:0px;border-spacing:0;"><table border="0" cellpadding="0" cellspacing="0" class="module" data-role="module-button" data-type="button" role="module" style="table-layout:fixed;" width="100%" data-muid="04203ba1-8a0c-4dd3-a939-91fbc3704996">
      <tbody>
        <tr>
          <td align="left" bgcolor="" class="outer-td" style="padding:0px 0px 0px 0px;">
            <table border="0" cellpadding="0" cellspacing="0" class="wrapper-mobile" style="text-align:center;">
              <tbody>
                <tr>
                <td align="center" bgcolor="#f88524" class="inner-td" style="border-radius:6px; font-size:16px; text-align:left; background-color:inherit;">
                  <a href="" style="background-color:#f88524; border:1px solid #ed8d15; border-color:#ed8d15; border-radius:8px; border-width:1px; color:#ffffff; display:inline-block; font-size:14px; font-weight:normal; letter-spacing:0px; line-height:normal; padding:8px 45px 8px 45px; text-align:center; text-decoration:none; border-style:solid; font-family:arial black, helvetica, sans-serif;" target="_blank">Share</a>
                </td>
                </tr>
              </tbody>
            </table>
          </td>
        </tr>
      </tbody>
    </table></td>
        </tr>
      </tbody>
    </table></td>
      </tr>
    </tbody>
  </table><table border="0" cellpadding="0" cellspacing="0" align="center" width="100%" role="module" data-type="columns" style="padding:0px 0px 0px 0px;" bgcolor="#F4F4F4" data-distribution="1">
    <tbody>
      <tr role="module-content">
        <td height="100%" valign="top"><table width="580" style="width:580px; border-spacing:0; border-collapse:collapse; margin:0px 10px 0px 10px;" cellpadding="0" cellspacing="0" align="left" border="0" bgcolor="" class="column column-0">
      <tbody>
        <tr>
          <td style="padding:0px;margin:0px;border-spacing:0;"><table class="module" role="module" data-type="code" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="e1276df8-f9d6-48d7-b295-ef63a555c437.1">
    <tbody>
      <tr>
        <td height="100%" valign="top" role="module-content"><div style="font-size:6px; line-height:10px; padding:20px 100px 2px 20px;" valign="top" align="left"><img class="max-width" border="0" style="float:left; color:#000000; text-decoration:none; font-family:Helvetica, arial, sans-serif; font-size:16px;" width="35" alt="" data-proportionally-constrained="true" data-responsive="false" src="http://cdn.mcauto-images-production.sendgrid.net/dfefe54e0a719529/98c35cab-5377-4b44-aebf-cb81a2c0fc10/63x59.PNG" height="33"></div>
<div style="font-family: inherit; text-align: inherit"><span style="font-size: 20px"><strong>Facts</strong></span></div>
<div style="font-family: inherit; text-align: inherit">Key information aggregated from trusted sources</div></td>
      </tr>
    </tbody>
  </table></td>
        </tr>
      </tbody>
    </table></td>
      </tr>
    </tbody>
  </table><table border="0" cellpadding="0" cellspacing="0" align="center" width="100%" role="module" data-type="columns" style="padding:0px 20px 0px 0px;" bgcolor="#F4F4F4" data-distribution="1">
    <tbody>
      <tr role="module-content">
        <td height="100%" valign="top"><table width="560" style="width:560px; border-spacing:0; border-collapse:collapse; margin:0px 10px 0px 10px;" cellpadding="0" cellspacing="0" align="left" border="0" bgcolor="" class="column column-0">
      <tbody>
        <tr>
          <td style="padding:0px;margin:0px;border-spacing:0;"><table class="module" role="module" data-type="text" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="dbd282bf-ccf5-408f-b939-68ad4831a17a" data-mc-module-version="2019-10-22">
    <tbody>
      <tr>
        <td style="padding:10px 0px 10px 30px; line-height:22px; text-align:inherit;" height="100%" valign="top" bgcolor="" role="module-content"><div><div style="font-family: inherit; text-align: inherit">"Federal health officials are poised to take the final steps on Saturday to clear the Moderna and Pfizer BioNTech coronavirus vaccines for very young children -- the only age group in the United States that does not yet have a vaccine option available."</div>
<div style="font-family: inherit; text-align: inherit"><span style="color: #ed8d15"><strong>Carly Olson</strong></span></div><div></div></div></td>
      </tr>
    </tbody>
  </table></td>
        </tr>
      </tbody>
    </table></td>
      </tr>
    </tbody>
  </table><table border="0" cellpadding="0" cellspacing="0" align="center" width="100%" role="module" data-type="columns" style="padding:0px 20px 0px 0px;" bgcolor="#F4F4F4" data-distribution="1">
    <tbody>
      <tr role="module-content">
        <td height="100%" valign="top"><table width="560" style="width:560px; border-spacing:0; border-collapse:collapse; margin:0px 10px 0px 10px;" cellpadding="0" cellspacing="0" align="left" border="0" bgcolor="" class="column column-0">
      <tbody>
        <tr>
          <td style="padding:0px;margin:0px;border-spacing:0;"><table class="module" role="module" data-type="text" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="dbd282bf-ccf5-408f-b939-68ad4831a17a.1" data-mc-module-version="2019-10-22">
    <tbody>
      <tr>
        <td style="padding:10px 0px 10px 30px; line-height:22px; text-align:inherit;" height="100%" valign="top" bgcolor="" role="module-content"><div><div style="font-family: inherit; text-align: inherit">"than a year and a half since vaccines began rolling out for adults, kids under 5 are the last group eligible to be vaccinated."</div>
<div style="font-family: inherit; text-align: inherit"><span style="color: #ed8d15"><strong>Nathaniel Weixel</strong></span></div><div></div></div></td>
      </tr>
    </tbody>
  </table></td>
        </tr>
      </tbody>
    </table></td>
      </tr>
    </tbody>
  </table><table class="module" role="module" data-type="divider" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="0f4c8f64-f0d0-40c5-be6a-52f407ac811b">
    <tbody>
      <tr>
        <td style="padding:0px 20px 0px 20px;" role="module-content" height="100%" valign="top" bgcolor="">
          <table border="0" cellpadding="0" cellspacing="0" align="center" width="100%" height="2px" style="line-height:2px; font-size:2px;">
            <tbody>
              <tr>
                <td style="padding:0px 0px 2px 0px;" bgcolor="#c6c5c5"></td>
              </tr>
            </tbody>
          </table>
        </td>
      </tr>
    </tbody>
  </table><table border="0" cellpadding="0" cellspacing="0" align="center" width="100%" role="module" data-type="columns" style="padding:0px 0px 0px 0px;" bgcolor="#F4F4F4" data-distribution="1">
    <tbody>
      <tr role="module-content">
        <td height="100%" valign="top"><table width="580" style="width:580px; border-spacing:0; border-collapse:collapse; margin:0px 10px 0px 10px;" cellpadding="0" cellspacing="0" align="left" border="0" bgcolor="" class="column column-0">
      <tbody>
        <tr>
          <td style="padding:0px;margin:0px;border-spacing:0;"><table class="module" role="module" data-type="code" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="e1276df8-f9d6-48d7-b295-ef63a555c437.1.1">
    <tbody>
      <tr>
        <td height="100%" valign="top" role="module-content"><div style="font-size:6px; line-height:10px; padding:20px 100px 2px 20px;" valign="top" align="left">
          <img class="max-width" border="0" style="float:left; color:#000000; text-decoration:none; font-family:Helvetica, arial, sans-serif; font-size:16px;" width="35" alt="" data-proportionally-constrained="true" data-responsive="false" src="http://cdn.mcauto-images-production.sendgrid.net/dfefe54e0a719529/6fa291f5-c811-46a8-83e1-05d2d60399c9/61x63.PNG" height="36">
        </div>
<div style="font-family: inherit; text-align: inherit"><span style="font-size: 20px"><strong>Opinions</strong></span></div>
<div style="font-family: inherit; text-align: inherit">Views across the spectrum</div></td>
      </tr>
    </tbody>
  </table></td>
        </tr>
      </tbody>
    </table></td>
      </tr>
    </tbody>
  </table><table border="0" cellpadding="0" cellspacing="0" align="center" width="100%" role="module" data-type="columns" style="padding:0px 20px 0px 0px;" bgcolor="#F4F4F4" data-distribution="1">
    <tbody>
      <tr role="module-content">
        <td height="100%" valign="top"><table width="560" style="width:560px; border-spacing:0; border-collapse:collapse; margin:0px 10px 0px 10px;" cellpadding="0" cellspacing="0" align="left" border="0" bgcolor="" class="column column-0">
      <tbody>
        <tr>
          <td style="padding:0px;margin:0px;border-spacing:0;"><table class="module" role="module" data-type="text" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="dbd282bf-ccf5-408f-b939-68ad4831a17a.2" data-mc-module-version="2019-10-22">
    <tbody>
      <tr>
        <td style="padding:10px 0px 10px 30px; line-height:22px; text-align:inherit;" height="100%" valign="top" bgcolor="" role="module-content"><div><div style="font-family: inherit; text-align: inherit; margin-left: 0px"><a href="https://emojipedia.org/blue-heart/" title="&lt;br&gt;&lt;h3 class=&quot;LC20lb MBeuO DKV0Md&quot; style=&quot;font-weight: 400; margin: 0px 0px 3px; padding: 5px 0px 0px; font-size: 20px; line-height: 1.3; font-family: Roboto, arial, sans-serif; display: inline-block;&quot;&gt;💙&lt;/h3&gt;"><span style="color: #8ab4f8; text-decoration-line: none; text-decoration-thickness: initial; text-decoration-style: initial; text-decoration-color: initial; -webkit-tap-highlight-color: rgba(255, 255, 255, 0.1); outline-color: initial; outline-style: initial; outline-width: 0px; font-family: Roboto, arial, sans-serif; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 400; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; margin-top: 0px; margin-right: 0px; margin-bottom: 3px; margin-left: 0px; padding-top: 5px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; line-height: 1.3; display: inline-block; background-color: rgb(244, 244, 244); font-size: 17px">💙</span></a> <span style="font-size: 16px; color: #908888"><strong>Left Leaning</strong></span></div>
<div style="font-family: inherit; text-align: inherit">"Many people have put the pandemic behind them, but for the youngest children, the threat posed by this virus still looms. A Kaiser Family Foundation survey from April shows just 18% of parents say they will get their child under 5 vaccinated as soon as a Covid-19 vaccine is authorized in their age group. The next hurdle will be to educate parents and caregivers and to address all their questions and concerns about these vaccines"</div>
<div style="font-family: inherit; text-align: inherit"><span style="color: #ed8d15"><strong>Opinion Syra Madad, CNN</strong></span></div><div></div></div></td>
      </tr>
    </tbody>
  </table></td>
        </tr>
      </tbody>
    </table></td>
      </tr>
    </tbody>
  </table><table border="0" cellpadding="0" cellspacing="0" align="center" width="100%" role="module" data-type="columns" style="padding:0px 20px 0px 0px;" bgcolor="#F4F4F4" data-distribution="1">
    <tbody>
      <tr role="module-content">
        <td height="100%" valign="top"><table width="560" style="width:560px; border-spacing:0; border-collapse:collapse; margin:0px 10px 0px 10px;" cellpadding="0" cellspacing="0" align="left" border="0" bgcolor="" class="column column-0">
      <tbody>
        <tr>
          <td style="padding:0px;margin:0px;border-spacing:0;"><table class="module" role="module" data-type="text" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="dbd282bf-ccf5-408f-b939-68ad4831a17a.2.1" data-mc-module-version="2019-10-22">
    <tbody>
      <tr>
        <td style="padding:10px 0px 10px 30px; line-height:22px; text-align:inherit;" height="100%" valign="top" bgcolor="" role="module-content"><div><div style="font-family: inherit; text-align: inherit; margin-left: 0px"><a href="https://emojipedia.org/orange-heart/" title="&lt;br&gt;&lt;h3 class=&quot;LC20lb MBeuO DKV0Md&quot; style=&quot;font-weight: 400; margin: 0px 0px 3px; padding: 5px 0px 0px; font-size: 20px; line-height: 1.3; font-family: Roboto, arial, sans-serif; display: inline-block;&quot;&gt;🧡&lt;/h3&gt;"><span style="color: #8ab4f8; text-decoration-line: none; text-decoration-thickness: initial; text-decoration-style: initial; text-decoration-color: initial; -webkit-tap-highlight-color: rgba(255, 255, 255, 0.1); outline-color: initial; outline-style: initial; outline-width: 0px; font-family: Roboto, arial, sans-serif; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 400; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; margin-top: 0px; margin-right: 0px; margin-bottom: 3px; margin-left: 0px; padding-top: 5px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; line-height: 1.3; display: inline-block; background-color: rgb(244, 244, 244); font-size: 17px">🧡</span></a> <span style="font-size: 16px; color: #908888"><strong>Moderate</strong></span></div>
<div style="font-family: inherit; text-align: inherit">"Dr. Peter Marks, FDA's vaccine chief, opened the meeting with data showing a "quite troubling surge" in young children's hospitalizations during the omicron wave, and noted 442 children under 4 have died during the pandemic. That's far fewer than adult deaths, but should not be dismissed in considering the need for vaccinating the youngest kids, he said."</div>
<div style="font-family: inherit; text-align: inherit"><span style="color: #ed8d15"><strong>Lindsey Tanner, Huffington Post</strong></span></div><div></div></div></td>
      </tr>
    </tbody>
  </table></td>
        </tr>
      </tbody>
    </table></td>
      </tr>
    </tbody>
  </table><div data-role="module-unsubscribe" class="module" role="module" data-type="unsubscribe" style="color:#444444; font-size:12px; line-height:20px; padding:16px 16px 16px 16px; text-align:Center;" data-muid="4e838cf3-9892-4a6d-94d6-170e474d21e5"><div class="Unsubscribe--addressLine"></div><p style="font-size:12px; line-height:20px;"><a target="_blank" class="Unsubscribe--unsubscribeLink zzzzzzz" href="{{{unsubscribe}}}" style="">Unsubscribe</a> - <a href="{{{unsubscribe_preferences}}}" target="_blank" class="Unsubscribe--unsubscribePreferences" style="">Unsubscribe Preferences</a></p></div></td>
                                      </tr>
                                    </table>
                                    <!--[if mso]>
                                  </td>
                                </tr>
                              </table>
                            </center>
                            <![endif]-->
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>
        </div>
      </center>
    </body>
  </html>"""
      )
  ]

  # message.template_id = template_id
  # message.dynamic_template_data=json.loads(hydrateNewsletterRes.newsletter)

  # message.dynamic_template_data =  {
  #   "Topic_Name": "TOPIC NAME",
  #   "Story_Title": "TITLE",
  #   "Story_Content": "SUMMARY",
  #   "Picture": "PICTURE",
  #   "Fact_Content1": "FACT 1",
  #   "Fact_Author": "AUTHOR",
  #   "Fact_Content2": "FACT 2",
  #   "Fact_Author2": "AUTHOR",
  #   "View_Type1": "Left Leaning",
  #   "Opinion_Content1": "OPINION",
  #   "Opinion_Author1": "AUTHOR",
  #   "View_Type2": "Right Leaning",
  #   "Opinion_Content2": "OPINION",
  #   "Opinion_Author2": "AUTHOR",
  # }

  logger.info("MESAGGEEEEEEEE")
  logger.info(message)
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
  newsletter = {
    "Topic_Name": topicPages[0].TopicName,
    "Story_Title": topicPages[0].Title,
    "Story_Content": topicPages[0].MDSSummary,
    "Picture": topicPages[0].ImageURL,
    "Fact_Content1": topicPages[0].Facts[0].Quote.Text,
    "Fact_Author": topicPages[0].Facts[0].Quote.Author,
    "Fact_Content2": topicPages[0].Facts[1].Quote.Text,
    "Fact_Author2": topicPages[0].Facts[0].Quote.Author,
    "View_Type1": "Left Leaning",
    "Opinion_Content1": topicPages[0].Opinions[0].Quote.Text,
    "Opinion_Author1": topicPages[0].Opinions[0].Quote.Author,
    "View_Type2": "Right Leaning",
    "Opinion_Content2": topicPages[0].Opinions[1].Quote.Text,
    "Opinion_Author2": topicPages[0].Opinions[1].Quote.Author,
  }

  logger.info("NEWSLETTER")
  logger.info(json.dumps(newsletter))

  # Returns the populated variables
  return HydrateNewsletterResponse(
    newsletter=json.dumps(newsletter),
    error=None,
  )




