import mailchimp_transactional as MailchimpTransactional
from mailchimp_transactional.api_client import ApiClientError

def run():
  try:
    mailchimp = MailchimpTransactional.Client('IbRJVT9R9C9JBt6gUA-E3g')
    response = mailchimp.users.ping()
    print('API called successfully: {}'.format(response))
  except ApiClientError as error:
    print('An exception occurred: {}'.format(error.text))

run()