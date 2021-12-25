from dataclasses import dataclass
import dataclasses
import json

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

@dataclass
class NewsletterConfig:
  DeliveryTime: time.time
  DeliveryDays: List[Day]
  RecurrenceAmount: int
  RecurrenceType: NewsletterRecurrenceType
  IsEnabled: bool

@dataclass
class ArticleInfo:
  Id: int
  Title: str
  Summary: str
  TopicName: str
  ImageURL: str
  TopPassage: str

@dataclass
class TopicInfo:
  TopicID: int
  TopicName: str
  PrimaryTopicName: str
  TopicPageURL: str

@dataclass
class Quote:
  Text: str
  SourceName: str
  SourceURL: str
  ImageURL: str
  Polarization: bool
  Timestamp: time.time
  ArticleID: int

@dataclass
class TimelineSegment:
  Quote: Quote

@dataclass
class Fact:
 Quote: Quote

@dataclass
class Opinion:
  Quote: Quote

@dataclass
class TopicPage:
  Title: str
  MDSSummary: str
  Facts: List[Fact]
  Opinions: List[Opinion]
  Timeline: List[TimelineSegment]
  TopArticleID: int
  TopicID: int

@dataclass
class TopicModal:
  Topic: str
  TopicTitle: str
  Summary: str
  Image: str
  Facts: List[Fact]

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


###
#
# ArticleRec
#
###

@dataclass
class HelloWorldRequest:
  name: str

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
  error: Exception

@dataclass_json
@dataclass
class PopulateArticlesResponse:
  num_articles_populated: int
  num_errors: int

@dataclass
class Article:
  id: Optional[int]
  url: Optional[str]
  authors: Optional[List[str]]
  topic: Optional[int]
  parentTopic: Optional[int]
  text: Optional[str]
  title: Optional[str]
  date: Optional[time.time]
  imageURL: Optional[str]
  polarizationScore: Optional[float]
  topPassage: Optional[str]
  topFact: Optional[str]

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
  articleIds: Optional[List[int]]

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

@dataclass_json
@dataclass
class GetRecommendedTopicsForUserResponse:
  topics: List[TopicInfo]


###
#
# User
#
###




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


