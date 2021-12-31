from dataclasses import *
import dataclasses
import json

from nltk import data

from marshmallow import EXCLUDE, fields, pre_dump, Schema, validate
import requests
import desert
from enum import Enum
from typing import List, Optional
import time
from dataclasses_json import dataclass_json

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
  FirebaseAuthID: int
  Username: str
  FirstName: str
  LastName: str
  EmailAddress: str


class NewsletterRecurrenceType(Enum):
  DAILY = 1
  WEEKLY = 2
  MONTHLY = 3

class Day(Enum):
  MONDAY = 1
  TUESDAY = 2
  WEDNESDAY = 3
  THURSDAY = 4
  FRIDAY = 5
  SATURDAY = 6
  SUNDAY = 7

@dataclass_json
@dataclass
class NewsletterConfig:
  DeliveryTime: time.time
  DeliveryDays: List[Day]
  RecurrenceAmount: int
  RecurrenceType: NewsletterRecurrenceType
  IsEnabled: bool

@dataclass_json
@dataclass
class ArticleInfo:
  Id: int
  Title: str
  Summary: str
  TopicName: str
  ImageURL: str
  TopPassage: str

@dataclass_json
@dataclass
class TopicInfo:
  TopicID: Optional[int]
  TopicName: str
  ParentTopicName: str

@dataclass_json
@dataclass
class Quote:
  Text: str
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
# TopicModel
#
###

@dataclass
class CreateTopicsRequest:
  topics: List[TopicInfo]

@dataclass_json
@dataclass
class CreateTopicsResponse:
  ids: List[int]
  error: Exception

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

@dataclass
class SearchDocumentsByTopicRequest:
  topic_num: int
  num_docs: int

@dataclass_json
@dataclass
class SearchDocumentsByTopicResponse:
  doc_ids: List[int]
  doc_scores: List[int]
  error: Optional[Exception]

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

@dataclass
class QueryDocumentsRequest:
  query: str
  num_docs: int
  return_docs: bool
  use_index: bool
  ef: int
  tokenizer: str

@dataclass_json
@dataclass
class QueryDocumentsResponse:
  doc_scores: List[int]
  doc_ids: List[int]
  error: Exception

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

@dataclass
class GetDocumentTopicRequest:
  doc_ids: List[int]
  reduced: bool
  num_topics: int

@dataclass_json
@dataclass
class GetDocumentTopicResponse:
  topic_num: int
  topic_score: float
  topic_word: str
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

@dataclass_json
@dataclass
class Article:
  id: Optional[int]
  url: str
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

@dataclass_json
@dataclass
class FetchArticlesResponse:
  articleList: Optional[List[Article]]
  error: Exception

@dataclass
class HydrateArticleRequest:
  url: List[str]

@dataclass_json
@dataclass
class HydrateArticleResponse:
  article: Article
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
class GetTopicPageByURLRequest:
  source: str

@dataclass
class GetTopicPageByArticleIDRequest:
  source: str

@dataclass
class GetTopicPageBySearchStringRequest:
  source: str

@dataclass
class GetTopicPageByTopicIDRequest:
  source: str

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
# User
#
###

@dataclass
class CreateUserRequest:
  firstName: str
  lastName: str
  email: str
  firebaseAuthId: str

@dataclass_json
@dataclass
class CreateUserResponse:
  user: User
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
  topic: str

@dataclass_json
@dataclass
class FollowTopicResponse:
  error: Exception

@dataclass
class UnfollowTopicRequest:
  userId: int
  topic: str

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

@dataclass
class GetRecommendedTopicsForUserRequest:
  user_id: int
  num_topics: int = 5

@dataclass_json
@dataclass
class GetRecommendedTopicsForUserResponse:
  topics: List[TopicInfo]


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


