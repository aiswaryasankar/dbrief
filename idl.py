from dataclasses import *
import dataclasses
import json

from nltk import data

# from marshmallow import EXCLUDE, fields, pre_dump, Schema, validate
import requests
import desert
from enum import Enum
from typing import List, Optional
import time
from dataclasses_json import dataclass_json
import typing

"""
  This file is a bit unconventional, but it will store all of the entity definitions across each of the services. Thus there will be one source of truth / common location for all the request, response, api definitions to work with.
"""

###
#
# Entities
#
###

@dataclass_json
@dataclass
class User:
  FirebaseAuthID: str
  Username: str
  FirstName: str
  LastName: str
  Email: str

@dataclass_json
@dataclass
class TopicInfo:
  TopicID: Optional[int]
  TopicName: str
  ParentTopicName: str

@dataclass_json
@dataclass
class NewsletterConfigV1:
  NewsletterConfigId: Optional[int]
  UserID: int
  DeliveryTime: typing.Literal['MORNING', 'AFTERNOON', 'EVENING']
  RecurrenceType: typing.Literal['DAILY', 'WEEKLY', 'MONTHLY']
  IsEnabled: bool
  TopicsFollowed: List[int]

@dataclass_json
@dataclass
class NewsletterConfigV2:
  DeliveryTime: time.time
  DeliveryDays: List[typing.Literal['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']]
  RecurrenceType: typing.Literal['DAILY', 'WEEKLY', 'MONTHLY']
  IsEnabled: bool
  TopicsFollowed: List[int]

@dataclass_json
@dataclass
class ArticleInfo:
  Id: int
  Title: str
  TopicName: str
  ImageURL: str
  TopPassage: str

@dataclass_json
@dataclass
class Article:
  url: str
  id: Optional[int] = ""
  authors: Optional[List[str]] = ""
  topic: Optional[str] = ""
  parentTopic: Optional[str] = ""
  text: Optional[str] = ""
  title: Optional[str] = ""
  date: Optional[time.time] = ""
  imageURL: Optional[str] = ""
  polarizationScore: Optional[float] = 0.0
  topPassage: Optional[str]= ""
  topFact: Optional[str] = ""

@dataclass_json
@dataclass
class Quote:
  Text: str
  Author: str
  SourceName: str
  SourceURL: str
  ImageURL: str
  Polarization: float
  Timestamp: time.time
  ArticleID: int

@dataclass_json
@dataclass
class TimelineSegment:
  Quote: Quote

@dataclass_json
@dataclass
class Fact:
 Quote: Quote

@dataclass_json
@dataclass
class Opinion:
  Quote: Quote

@dataclass_json
@dataclass
class TopicPage:
  Title: str
  ImageURL: str
  MDSSummary: str
  Facts: List[Fact]
  Opinions: List[Opinion]
  Timeline: List[TimelineSegment]
  TopArticleID: int
  TopicID: int

@dataclass_json
@dataclass
class TopicModal:
  Topic: str
  TopicTitle: str
  Summary: str
  Image: str
  Facts: List[Fact]

@dataclass_json
@dataclass
class Author:
  ID: int
  Name: str


###
#
# TopicModelV2
#
###

# @dataclass
# class TrainAndIndexTopicModelRequestV2:
#   documents: List[str]
#   embedding_model: str
#   speed: str
#   doc_ids: List[str]
#   keep_documents: bool


# @dataclass
# class GetDocumentTopicRequestV2:
#   documents: List[str]

# @dataclass_json
# @dataclass
# class GetDocumentTopicResponseV2:
#   topicInfos: List[TopicInfo]
#   error: Exception

# @dataclass_json
# @dataclass
# class GetTopicsResponseV2:
#   topicInfos: List[TopicInfo]
#   error: Optional[Exception]

# # TO UPDATE - will return document text using get_representative_docs
# # For all other use cases use query_documents on Top2Vec passing in topic as a string
# @dataclass
# class SearchDocumentsByTopicRequestV2:
#   topic_num: int

# @dataclass_json
# @dataclass
# class SearchDocumentsByTopicResponseV2:
#   documents: List[str]
#   error: Optional[Exception]

# # Same using find_topics instead
# # Optionally update the response to return TopicInfo instead
# @dataclass
# class SearchTopicsRequestV2:
#   search_term: str
#   num_topics: int

# @dataclass_json
# @dataclass
# class SearchTopicsResponseV2:
#   topicInfos: List[TopicInfo]
#   error: Exception


###
#
# TopicModel
#
###

# Same
@dataclass
class CreateTopicsRequest:
  topics: List[TopicInfo]

@dataclass_json
@dataclass
class CreateTopicsResponse:
  ids: List[int]
  error: Exception

# TopicIds are indices into the topic database
# Same
@dataclass
class FetchTopicInfoBatchRequest:
  topicIds: Optional[List[int]] = field(default_factory=list)
  topicNames: Optional[List[str]] = field(default_factory=list)

@dataclass_json
@dataclass
class FetchTopicInfoBatchResponse:
  topics: List[TopicInfo]
  error: Exception

# Same but optionally update response to return TopicInfo instead
@dataclass
class GetTopicsRequest:
  num_topics: int
  reduced: bool

@dataclass_json
@dataclass
class GetTopicsResponse:
  topic_words: List[str]
  topic_nums: List[int]
  error: Optional[Exception]

# TO UPDATE - will return document text using get_representative_docs
# For all other use cases use query_documents on Top2Vec passing in topic as a string
@dataclass
class SearchDocumentsByTopicRequest:
  topic_num: int
  num_docs: Optional[int]

@dataclass_json
@dataclass
class SearchDocumentsByTopicResponse:
  doc_ids: List[int]
  doc_scores: List[int]
  error: Optional[Exception]

# Same using find_topics instead
# Optionally update the response to return TopicInfo instead
@dataclass
class SearchTopicsRequest:
  keywords: List[str]
  num_topics: int

@dataclass_json
@dataclass
class SearchTopicsResponse:
  topics_words: List[str]
  topic_scores: List[float]
  topic_nums: List[int]
  error: Exception

# Same
@dataclass
class AddDocumentRequest:
  documents: List[str]
  doc_ids: List[int]
  tokenizer: str
  use_embedding_model_tokenizer: bool

@dataclass_json
@dataclass
class AddDocumentResponse:
  error: Exception

# Same
@dataclass
class QueryDocumentsRequest:
  query: str
  num_docs: int
  return_docs: bool
  use_index: bool
  ef: int

@dataclass_json
@dataclass
class QueryDocumentsResponse:
  doc_scores: List[int]
  doc_ids: List[int]
  error: Exception

# Will have a V2 endpoint with a few additional fields
@dataclass
class TrainAndIndexTopicModelRequest:
  documents: List[str]
  embedding_model: str
  speed: str
  doc_ids: List[str]
  keep_documents: bool

@dataclass_json
@dataclass
class TrainAndIndexTopicModelResponse:
  error: Exception

# Will need a V2 endpoint since you pass in the document not doc_ids, will call transform
# Optionally update response to return a TopicInfo instead
@dataclass
class GetDocumentTopicRequest:
  doc_ids: List[int] = field(default_factory=list)
  reduced: bool = False
  num_topics: int = 1

@dataclass_json
@dataclass
class GetDocumentTopicResponse:
  topic_num: int
  topic_score: int
  topic_word: str
  error: Exception

@dataclass
class GetDocumentTopicBatchRequest:
  doc_ids: List[int] = field(default_factory=list)
  num_topics: int = 1

@dataclass
class DocumentTopicInfo:
  doc_id: int
  topicInfo: TopicInfo


@dataclass_json
@dataclass
class GetDocumentTopicBatchResponse:
  documentTopicInfos: List[DocumentTopicInfo]
  error: Exception


@dataclass_json
@dataclass
class GenerateTopicPairsResponse:
  topic_pairs: List[TopicInfo]


###
#
# ArticleRec
#
###

@dataclass
class HelloWorldRequest:
  name: str = "aiswarya"

@dataclass_json
@dataclass
class HelloWorldResponse:
  name: str

@dataclass
class PopulateArticleRequest:
  url: Optional[str]

@dataclass_json
@dataclass
class PopulateArticleResponse:
  url: Optional[str]
  id: Optional[int]
  error: Exception

@dataclass_json
@dataclass
class PopulateArticlesResponse:
  num_articles_populated: int
  num_errors: int

@dataclass
class SaveArticleRequest:
  article: Optional[Article]

@dataclass_json
@dataclass
class SaveArticleResponse:
  id: int
  error: Exception
  created: bool

@dataclass
class FetchArticlesRequest:
  articleIds: Optional[List[int]] = field(default_factory=list)
  articleUrls: Optional[List[str]] = field(default_factory=str)

@dataclass_json
@dataclass
class FetchArticlesResponse:
  articleList: Optional[List[Article]]
  error: Exception

@dataclass
class HydrateArticleRequest:
  url: str

@dataclass_json
@dataclass
class HydrateArticleResponse:
  article: Optional[Article]
  url: Optional[str]
  error: Exception

@dataclass
class ArticleBackfillRequest:
  force_update: bool
  fields: Optional[List[str]]

@dataclass_json
@dataclass
class ArticleBackfillResponse:
  num_updates: int
  error: Exception

@dataclass
class QueryArticleRequest:
  field: str

@dataclass_json
@dataclass
class QueryArticleResponse:
  articles: List[Article]
  error: Exception


###
#
# PolarityModel
#
###

@dataclass
class GetDocumentPolarityRequest:
  query: Optional[str]
  source: Optional[str]

@dataclass_json
@dataclass
class GetDocumentPolarityResponse:
  polarity_score: Optional[float]
  error: Exception

@dataclass
class GetDocumentPolarityBatchRequest:
  queryList: Optional[List[str]]
  source: Optional[str]

@dataclass_json
@dataclass
class GetDocumentPolarityBatchResponse:
  polarity_score: Optional[List[float]]
  error: Exception

###
#
# PassageModel
#
###

@dataclass
class GetFactsRequest:
  article_text: str

@dataclass_json
@dataclass
class GetFactsResponse:
  facts: List[str]
  error: Exception

@dataclass
class GetTopPassageRequest:
  article_text: str

@dataclass_json
@dataclass
class GetTopPassageResponse:
  passage: str
  error: Exception

###
#
# TopicFeed
#
###

@dataclass
class GetTopicPageRequest:
  url: str = ""
  articleId: int = 0
  text: str = ""
  topicName: str = ""

  # def __post_init__(self):
  #   """
  #     Escape the double quotes from the text input to pass validation
  #   """
  #   print(self.text)
  #   if self.text and self.text != "":
  #     self.text = self.text.replace('"','\\"')

@dataclass_json
@dataclass
class GetTopicPageResponse:
  topic_page: TopicPage
  error: Exception

@dataclass
class WhatsHappeningRequest:
  user_id: int

@dataclass_json
@dataclass
class WhatsHappeningResponse:
  articles: List[ArticleInfo]
  error: Exception


###
#
# UserPreferences
#
###

@dataclass
class CreateUserRequest:
  user: User

@dataclass_json
@dataclass
class CreateUserResponse:
  userId: int
  error: Exception

@dataclass
class GetUserRequest:
  userId: int

@dataclass_json
@dataclass
class GetUserResponse:
  user: User
  error: Exception

@dataclass
class FollowTopicRequest:
  userId: int
  topicId: int
  forNewsletter: Optional[bool] = False

@dataclass_json
@dataclass
class FollowTopicResponse:
  userTopicId: int
  error: Exception

@dataclass
class UnfollowTopicRequest:
  userId: int
  topicId: int

@dataclass_json
@dataclass
class UnfollowTopicResponse:
  error: Exception

@dataclass
class GetTopicsForUserRequest:
  user_id: int

@dataclass_json
@dataclass
class GetTopicsForUserResponse:
  topics: List[TopicInfo]
  error: Exception

@dataclass_json
@dataclass
class GetTopicsYouFollowResponse:
  topics: List[str]
  error: Exception

@dataclass
class GetRecommendedTopicsForUserRequest:
  user_id: int
  num_topics: int = 5

@dataclass_json
@dataclass
class GetRecommendedTopicsForUserResponse:
  topics: List[TopicInfo]
  error: Exception


###
#
# MDSModel
#
###

@dataclass
class GetMDSSummaryRequest:
  articles: str


@dataclass_json
@dataclass
class GetMDSSummaryResponse:
  summary: str
  error: Exception

###
#
# HomeFeed
#
###



###
#
# Newsletter
#
###

@dataclass
class CreateNewsletterConfigForUserRequest:
  newsletterConfig: NewsletterConfigV1

@dataclass_json
@dataclass
class CreateNewsletterConfigForUserResponse:
  newsletterId: int
  error: Exception

@dataclass
class GetNewsletterConfigForUserRequest:
  userId: int

@dataclass_json
@dataclass
class GetNewsletterConfigForUserResponse:
  newsletterConfig: NewsletterConfigV1
  error: Exception

@dataclass
class UpdateNewsletterConfigForUserRequest:
  newsletterConfig: NewsletterConfigV1

@dataclass_json
@dataclass
class UpdateNewsletterConfigForUserResponse:
  error: Exception

@dataclass
class SendNewslettersBatchRequest:
  timeOfDay: typing.Literal['MORNING', 'AFTERNOON', 'EVENING']
  day: typing.Literal['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']

@dataclass_json
@dataclass
class SendNewslettersBatchResponse:
  newsletters_success: List[str]
  newsletters_failed: List[str]

@dataclass
class SendNewsletterRequest:
  userId: int
  userEmail: Optional[str]

@dataclass_json
@dataclass
class SendNewsletterResponse:
  error: Exception

@dataclass
class HydrateNewsletterRequest:
  newsletterConfigId: int

@dataclass_json
@dataclass
class HydrateNewsletterResponse:
  error: Exception


