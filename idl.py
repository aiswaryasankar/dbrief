from dataclasses import dataclass
import dataclasses
import json

from marshmallow import EXCLUDE, fields, pre_dump, Schema, validate
import requests
import desert
from enum import Enum
from typing import List, Optional
import time

"""
  This file is a bit unconventional, but it will store all of the entity definitions across each of the services. Thus there will be one source of truth / common location for all the request, response, api definitions to work with.
"""

### Topic Model
@dataclass
class AddDocumentRequest:
  documents: List[str]
  doc_ids: List[int]
  tokenizer: str
  use_embedding_model_tokenizer: bool

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

@dataclass
class GetDocumentTopicResponse:
  topic_num: int
  topic_score: float
  topic_word: str
  error: Exception

### Newsletter




### ArticleRec
@dataclass
class PopulateArticleRequest:
  url: Optional[str]

@dataclass
class PopulateArticleResponse:
  url: Optional[str]
  error: Exception

@dataclass
class PopulateArticlesResponse:
  num_articles_populated: int
  num_errors: int

@dataclass
class Article:
  id: Optional[int]
  url: Optional[str]
  authors: Optional[List[str]]
  primaryTopic: Optional[int]
  secondaryTopic: Optional[int]
  text: Optional[str]
  title: Optional[str]
  date: Optional[time.time]
  summary: Optional[str]
  imageURL: Optional[str]
  polarizationScore: Optional[float]
  isOpinion: Optional[bool]

@dataclass
class SaveArticleRequest:
  article: Optional[Article]

@dataclass
class SaveArticleResponse:
  id: int
  error: Exception
  created: bool

@dataclass
class FetchAllArticlesResponse:
  articleList: Optional[List[Article]]
  error: Exception

### User




###





### Entities

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





