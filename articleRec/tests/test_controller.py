# from django import test
# from django.test import Client
# from django.test import TestCase
# from idl import *
# from articleRec.controller import *
# from datetime import datetime
# import time

# """
#   This file will handle testing out all the controller functions.
# """


# class ArticleRecControllerTest(TestCase):

#   def test_populate_articles_batch(self):
#     """
#       Test that you are able to populate articles in batch and not overwrite already hydrated data in the database.
#     """
#     # First call populate_articles_batch with a few URLS
#     res = populate_articles_batch(
#       PopulateArticlesBatchRequest(
#         urls=["https://www.nytimes.com/2022/01/03/world/europe/eu-hungary-threat.html","https://www.nytimes.com/2022/05/30/world/europe/ukraine-russia-chernihiv.html"]
#       )
#     )
#     self.assertEqual(res.num_errors, 0)
#     self.assertEqual(res.num_articles_populated, 2)

#     time.sleep(2)
#     # Then call it again and make sure it doesn't overwrite after sleeping for x seconds
#     res = populate_articles_batch(
#       PopulateArticlesBatchRequest(
#         urls=["https://www.nytimes.com/2022/01/03/world/europe/eu-hungary-threat.html","https://www.nytimes.com/2022/05/30/world/europe/ukraine-russia-chernihiv.html"]
#       )
#     )
#     self.assertEqual(res.num_errors, 0)
#     self.assertEqual(res.num_articles_populated, 0)



