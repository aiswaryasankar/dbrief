from dataclasses import dataclass
import dataclasses
import json

from marshmallow import EXCLUDE, fields, pre_dump, Schema, validate
import requests
import desert
from enum import Enum

"""
  This file is a bit unconventional, but it will store all of the entity definitions across each of the services. Thus there will be one source of truth / common location for all the request, response, api definitions to work with.
"""

### Topic Model
@dataclass
class AddDocumentRequest:
  documents: list(str)
  doc_ids: list(int)
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
  doc_scores: list(int)
  doc_ids: list(int)

@dataclass
class TrainAndIndexTopicModelRequest:
  documents: list(str)
  embedding_model: str
  speed: str
  doc_ids: list(str)
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
  doc_scores: list(int)
  doc_ids: list(int)

@dataclass
class GetDocumentTopicRequest:
  doc_ids: list(int)
  reduced: bool
  num_topics: int

@dataclass
class GetDocumentTopicResponse:
  topic_num: int
  topic_score: float
  topic_word: str


### Newsletter




### ArticleRec
@dataclass
class PopulateArticlesResponse:
  num_articles_populated: int
  num_errors: int

@dataclass
class SaveArticleRequest:
  id: int
  url: str
  authorID: int
  primaryTopicID: int
  secondaryTopicID: int
  text: str
  title: str
  date: time
  summary: str
  imageURL: str
  polarizationScore: float
  isOpinion: bool

@dataclass
class SaveArticleResponse:
  id: int
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

@dataclass
class Fact:
 Quote: Quote

@dataclass
class Opinion:
  Quote: Quote

@dataclass
class TimelineSegment:
  Quote: Quote

@dataclass
class NewsletterConfig:
  DeliveryTime: time
  DeliveryDays: list(Day)
  RecurrenceAmount: int
  RecurrenceType: NewsletterRecurrenceType
  IsEnabled: bool

@dataclass
class ArticleInfo:
  ID - int
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
class TopicPage:
  Title: str
  MDSSummary: str
  Facts: list(Fact)
  Opinions: list(Opinion)
  Timeline: list(TimelineSegment)
  TopArticleID: int
  TopicID: int

@dataclass
class TopicModal:
  Topic: str
  TopicTitle: str
  Summary: str
  Image: str
  Facts: list(Fact)

@dataclass
class Author:
  ID: int
  Name: str

@dataclass
class Quote:
  Text: str
  SourceName: str
  SourceURL: str
  ImageURL: str
  Polarization: bool
  Timestamp: time
  ArticleID: int





