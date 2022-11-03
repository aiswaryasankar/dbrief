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
  FirstName: str
  LastName: str
  Email: str
  UserId: Optional[int]= field(default_factory=int)

@dataclass_json
@dataclass
class TopicInfo:
  TopicID: Optional[int]
  TopicName: str
  ParentTopicName: str

@dataclass_json
@dataclass
class NewsletterConfigV1:
  UserID: int
  DeliveryTime: typing.Literal['MORNING', 'AFTERNOON', 'EVENING']
  RecurrenceType: typing.Literal['DAILY', 'WEEKLY', 'MONTHLY']
  IsEnabled: bool
  TopicsFollowed: List[TopicInfo]
  NewsletterConfigId: Optional[int]=""
  DayOfWeek: Optional[int]=0

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
  url: Optional[str] = ""
  id: Optional[int] = ""
  authors: Optional[List[str]] = ""
  topic: Optional[str] = ""
  parentTopic: Optional[str] = ""
  text: Optional[str] = ""
  title: Optional[str] = ""
  date: Optional[str] = ""
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
  TopArticleID: int
  TopicID: int
  TopicName: str
  IsTimeline: bool
  CreatedAt: str

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

@dataclass
class TrainAndIndexTopicModelRequestV2:
  documents: List[str]
  embedding_model: str
  speed: str
  doc_ids: List[str]
  keep_documents: bool


@dataclass
class GetDocumentTopicRequestV2:
  documents: List[str]

@dataclass_json
@dataclass
class GetDocumentTopicResponseV2:
  topicInfos: List[TopicInfo]
  error: Exception

@dataclass_json
@dataclass
class GetTopicsResponseV2:
  topicInfos: List[TopicInfo]
  error: Optional[Exception]

@dataclass
class DeleteTopicsRequest:
  num_days: int

@dataclass_json
@dataclass
class DeleteTopicsResponse:
  error: Exception


# TO UPDATE - will return document text using get_representative_docs
# For all other use cases use query_documents on Top2Vec passing in topic as a string
@dataclass
class SearchDocumentsByTopicRequestV2:
  topic_num: int

@dataclass_json
@dataclass
class SearchDocumentsByTopicResponseV2:
  documents: List[str]
  error: Optional[Exception]

# Same using find_topics instead
# Optionally update the response to return TopicInfo instead
@dataclass
class SearchTopicsRequestV2:
  search_term: str
  num_topics: int

@dataclass_json
@dataclass
class SearchTopicsResponseV2:
  topicInfos: List[TopicInfo]
  error: Exception


###
#
# TopicModel
#
###


@dataclass
class AddDocumentsElasticSearchRequest:
  documents: List[dict]

@dataclass_json
@dataclass
class AddDocumentsElasticSearchResponse:
  num_documents_added : int
  error : Exception

@dataclass
class DeleteDocumentsElasticSearchRequest:
  article_ids : List[int]

@dataclass_json
@dataclass
class DeleteDocumentsElasticSearchResponse:
  num_articles_deleted : int
  error : Exception

@dataclass
class QueryDocumentsElasticSearchRequest:
  query: str
  num_docs: int

@dataclass_json
@dataclass
class QueryDocumentsElasticSearchResponse:
  candidate_documents: List[dict]
  error: Exception

@dataclass
class AddDocumentsFaissRequest:
  documents: List[dict]

@dataclass_json
@dataclass
class AddDocumentsFaissResponse:
  num_documents_added : int
  error : Exception

@dataclass
class QueryDocumentsFaissRequest:
  query: str
  num_docs: int

@dataclass_json
@dataclass
class QueryDocumentsFaissResponse:
  candidate_documents: List[dict]
  error: Exception


@dataclass
class DeleteDocumentsFaissRequest:
  article_ids : List[int]

@dataclass_json
@dataclass
class DeleteDocumentsFAISSResponse:
  num_articles_deleted : int
  error : Exception

@dataclass
class DeleteDocumentsRequest:
  docIds: List[int]

@dataclass_json
@dataclass
class DeleteDocumentsResponse:
  numArticlesDeleted: int
  error: Exception

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
  topic_infos: Optional[List[TopicInfo]]
  error: Exception

# Same
@dataclass
class AddDocumentRequest:
  documents: List[str]
  doc_ids: List[int]
  tokenizer: str

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
  elastic_search_urls: List[str]
  faiss_urls: List[str]
  hnswlib_urls: List[str]
  doc_scores: List[int]
  doc_ids: List[int]
  error: Exception

@dataclass
class QueryDocumentsV2Request:
  query: str
  num_docs: int

@dataclass_json
@dataclass
class QueryDocumentsV2Response:
  docs: str
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
  topic: str
  parentTopic: str

@dataclass_json
@dataclass
class GetDocumentTopicBatchResponse:
  documentTopicInfos: List[DocumentTopicInfo]
  error: Exception


@dataclass_json
@dataclass
class GenerateTopicPairsResponse:
  topic_pairs: List[TopicInfo]

@dataclass_json
@dataclass
class QueryDocCountsResponse:
  numDocsMysql: int
  numDocsFAISS: int
  numDocsHNSWLib: int
  numDocsES: int


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
class PopulateArticlesBatchRequest:
  urls: Optional[List[str]]

@dataclass
class PopulateArticleRequest:
  url: Optional[str]
  source: Optional[str] = ""
  category: Optional[str] = ""

@dataclass_json
@dataclass
class PopulateArticleResponse:
  article: Optional[Article]
  id: Optional[int]
  url: Optional[str]
  error: Exception

@dataclass_json
@dataclass
class PopulateArticlesResponse:
  num_articles_populated: int
  num_duplicates: int
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
  numDays: Optional[int] = field(default_factory=int)


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
class HydrateArticlesBatchRequest:
  articles: Optional[List[Article]]

@dataclass_json
@dataclass
class HydrateArticlesBatchResponse:
  articles: Optional[List[Article]]
  error: Exception
  urls: Optional[List[str]] = field(default_factory=list)

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

@dataclass_json
@dataclass
class DeleteArticlesRequest:
  num_days: int

@dataclass_json
@dataclass
class DeleteArticlesResponse:
  num_articles_deleted: int
  error: Exception



###
#
# PolarityModel
#
###

@dataclass
class GetDocumentPolarityRequest:
  query: Optional[str]
  source: Optional[str] = ""

@dataclass_json
@dataclass
class GetDocumentPolarityResponse:
  polarity_score: Optional[float]
  error: Exception

@dataclass
class ArticlePolarity:
  article_id: int
  polarity_score: int

@dataclass
class GetDocumentPolarityBatchRequest:
  articleList: List[Article] = field(default_factory=list)
  source: Optional[str] = field(default_factory=str)

@dataclass_json
@dataclass
class GetDocumentPolarityBatchResponse:
  articlePolarities: Optional[List[ArticlePolarity]]
  error: Exception

@dataclass
class GetDocumentCauseRequest:
  query: Optional[str]

@dataclass_json
@dataclass
class GetDocumentCausesResponse:
  causeList: List[str]
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

@dataclass
class ArticleFact:
  article_id: int
  facts: List[str]

@dataclass
class ArticlePassage:
  article_id: int
  passage: str

@dataclass
class GetFactsBatchRequest:
  articleList: List[Article] = field(default_factory=list)

@dataclass_json
@dataclass
class GetFactsBatchResponse:
  articleFacts : List[ArticleFact]
  error: Exception

@dataclass
class GetTopPassageBatchRequest:
  articleList: List[Article] = field(default_factory=list)

@dataclass_json
@dataclass
class GetTopPassageBatchResponse:
  articlePassages: List[ArticlePassage]
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
  topicId: int = 0
  savePage : bool = False


@dataclass_json
@dataclass
class GetTopicPageResponse:
  topic_page: TopicPage
  error: Exception

@dataclass
class WhatsHappeningRequest:
  user_id: Optional[int] = 0

@dataclass_json
@dataclass
class WhatsHappeningResponse:
  articles: List[ArticleInfo]
  error: Exception

@dataclass
class DeleteTopicsByDateRangeRequest:
  num_days: int

@dataclass_json
@dataclass
class DeleteTopicsByDateRangeResponse:
  num_topics_deleted: int
  error: Exception


@dataclass
class SaveTopicPageRequest:
  topic: str
  topicId: int
  summary : str
  title : str
  imageURL : str
  urls : str
  topArticleId : int
  isTimeline : bool

@dataclass_json
@dataclass
class SaveTopicPageResponse:
  topicPageId: int
  error: Exception

@dataclass
class FetchTopicPageRequest:
  topic: str
  topicPageId: Optional[int] = 0
  topArticleId: Optional[int] = 0

@dataclass_json
@dataclass
class FetchTopicPageResponse:
  topic_page: TopicPage
  error: Exception

@dataclass
class FetchTopicPageBatchRequest:
  offset: int
  pageSize: int
  topics: Optional[List[str]]
  topicPageId: Optional[List[int]] = field(default_factory=list)

@dataclass_json
@dataclass
class FetchTopicPageBatchResponse:
  topicPages: List[TopicPage]
  error: Exception

@dataclass
class HydrateTopicPagesRequest:
  force_update: bool

@dataclass_json
@dataclass
class HydrateTopicPagesResponse:
  numPagesHydrated: int
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
  firebaseAuthId: Optional[str]=""
  userId: Optional[int]=0

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
  for_newsletter: Optional[bool]=False

@dataclass_json
@dataclass
class GetTopicsForUserResponse:
  topics: List[TopicInfo]
  error: Exception

@dataclass_json
@dataclass
class GetTopicsYouFollowResponse:
  topics: List[str]
  topicInfos: List[TopicInfo]
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

@dataclass
class GetMDSSummaryAndTitleRequest:
  articles: str
  include_title: Optional[bool] = True


@dataclass_json
@dataclass
class GetMDSSummaryAndTitleResponse:
  summary: str
  title: str
  error: Exception

###
#
# HomeFeed
#
###

@dataclass
class HydrateHomePageRequest:
  userId: int

@dataclass_json
@dataclass
class HydrateHomePageResponse:
  topicPages: List[TopicPage]
  error: Exception


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
  newsletterId: int
  error: Exception

@dataclass
class SendNewslettersBatchRequest:
  timeOfDay: typing.Literal['MORNING', 'AFTERNOON', 'EVENING']
  day: Optional[int]=0

@dataclass_json
@dataclass
class SendNewslettersBatchResponse:
  success_user_ids: List[int]
  failed_user_ids: List[int]

@dataclass
class SendNewsletterRequest:
  userId: Optional[int]=field(default_factory=int)

@dataclass_json
@dataclass
class SendNewsletterResponse:
  error: Exception

@dataclass
class HydrateNewsletterRequest:
  topicPages: List[TopicPage]

@dataclass_json
@dataclass
class HydrateNewsletterResponse:
  newsletter: str
  error: Exception

@dataclass
class QueryNewsletterConfigRequest:
  deliveryTime: typing.Literal['MORNING', 'AFTERNOON', 'EVENING']
  day: Optional[int]=0

@dataclass
class QueryNewsletterConfigResponse:
  newsletterConfigs: List[NewsletterConfigV1]
  error: Exception



###
#
# NewsInfoCard
#
###


@dataclass
class OpinionCard:
  uuid: str
  summary: str
  articleURLList: Optional[List[str]] = field(default_factory=list)
  articleTitleList: Optional[List[str]] = field(default_factory=list)

@dataclass
class NewsInfoCard:
  uuid: str
  title: str
  summary: str
  isPolitical: bool
  leftOpinionCard: Optional[OpinionCard]
  rightOpinionCard: Optional[OpinionCard]
  articleList: Optional[List[Article]] = field(default_factory=list)


@dataclass
class CreateNewsInfoCardRequest:
  article: Optional[Article]
  articleURL: Optional[str] = ''


@dataclass_json
@dataclass
class CreateNewsInfoCardResponse:
  newsInfoCard: NewsInfoCard
  error: Exception

@dataclass
class CreateNewsInfoCardRepoRequest:
  url : Optional[str]
  title : Optional[str]
  summary : Optional[str]
  image : Optional[str]
  source : Optional[str]
  publish_date : Optional[time.time]
  author : Optional[str]
  is_political : Optional[bool]
  topic : Optional[str]
  left_opinion_card_UUID : Optional[str]
  right_opinion_card_UUID : Optional[str]
  article_url_list : Optional[str]
  article_title_list : Optional[str]


@dataclass
class CreateNewsInfoCardBatchRequest:
  articleUrls: Optional[List[str]] = field(default_factory=list)
  articleList: Optional[List[Article]] = field(default_factory=list)

@dataclass_json
@dataclass
class CreateNewsInfoCardBatchResponse:
  newsInfoCards: List[NewsInfoCard]
  error: Exception

@dataclass
class CreateOpinionCardRequest:
  polarity : bool
  articleList : List[Article]
  summary : Optional[str] = ""

@dataclass_json
@dataclass
class CreateOpinionCardResponse:
  opinionCard : OpinionCard
  error : Exception

@dataclass
class FetchNewsInfoCardBatchRequest:
  offset: int
  pageSize: int

@dataclass_json
@dataclass
class FetchNewsInfoCardBatchResponse:
  newsInfoCards: List[NewsInfoCard]
  error: Exception

@dataclass
class FetchNewsInfoCardRequest:
  newsInfoCardUUID: str

@dataclass_json
@dataclass
class FetchNewsInfoCardResponse:
  newsInfoCard: NewsInfoCard
  error: Exception

@dataclass
class FetchOpinionCardRequest:
  opinionCardUUID: str

@dataclass_json
@dataclass
class FetchOpinionCardResponse:
  opinionCard: OpinionCard
  error: Exception


###############
#
#  Organizations
#
###############

@dataclass
class Organization:
  name: str
  image: str
  backgroundImage: str
  link: str
  description: str
  locationUUID: str
  uuid: Optional[str] = ""

@dataclass
class Location:
  name: str
  street: str
  city: str
  state: str
  zip: int
  country: str

@dataclass
class RankedOrganization:
  organization: Organization
  rank: int

@dataclass
class FetchOrgnizationsRequest:
  uuids: Optional[List[str]] = field(default_factory=list)
  causes: Optional[List[str]] = field(default_factory=list)

@dataclass_json
@dataclass
class FetchOrganizationsResponse:
  orgList: List[Organization]
  error: Exception

@dataclass
class FetchAllOrganizationsResponse:
  orgList: List[Organization]
  error: Exception

@dataclass
class RankOrganizationsForNewsInfoCardRequest:
  orgList: List[Organization]
  newsInfoCard: NewsInfoCard

@dataclass_json
@dataclass
class RankOrganizationsForNewsInfoCardResponse:
  rankedOrganizations: List[RankedOrganization]
  error: Exception

@dataclass
class CreateRecommendedOrgsForNewsInfoCardRepoRequest:
  newsInfoCardUUID: str
  organizationUUID: str
  rank: int

@dataclass_json
@dataclass
class CreateRecommendedOrgsForNewsInfoCardRepoResponse:
  error: Exception


@dataclass
class CreateOrganizationRequest:
  name: str
  description: str
  image: str
  backgroundImage: str
  location: Location
  url: str
  causes: List[str]
  email: str

@dataclass
class CreateOrganizationRepoRequest:
  name: str
  description: str
  image: str
  backgroundImage: str
  locationUUID: str
  url: str
  email: str

@dataclass
class CreateCausesForOrganizationRepoRequest:
  organizationUUID: str
  cause: str

@dataclass_json
@dataclass
class CreateCausesForOrganizationRepoResponse:
  error: Exception

@dataclass_json
@dataclass
class CreateOrganizationResponse:
  organizationUUID: str
  error: Exception
  organization: Optional[Organization] = None


@dataclass
class GenerateRecommendedOrgsForNewsInfoCardRequest:
  newsInfoCardUUID: Optional[str] = ""
  newsInfoCard: Optional[NewsInfoCard] = None

@dataclass_json
@dataclass
class GenerateRecommendedOrgsForNewsInfoCardResponse:
  orgList: List[RankedOrganization]
  error: Exception

@dataclass
class GetRecommendedOrgsForNewsInfoCardRequest:
  newsInfoCardUUID: Optional[str] = ""
  newsInfoCard: Optional[NewsInfoCard] = None

@dataclass_json
@dataclass
class GetRecommendedOrgsForNewsInfoCardResponse:
  orgList: List[RankedOrganization]
  error: Exception


@dataclass
class CreateLocationRequest:
  name: str
  street: str
  city: str
  state: str
  zip: int
  country: str


@dataclass_json
@dataclass
class CreateLocationResponse:
  uuid: str
  location: Location
  error: Exception


@dataclass
class FetchLocationRequest:
  name: Optional[str] = ""
  street: Optional[str] = ""
  city: Optional[str] = ""


@dataclass_json
@dataclass
class FetchLocationResponse:
  uuid: str
  location: Location
  error: Exception

@dataclass_json
@dataclass
class FetchLocationResponse:
  uuid: str
  location: Location
  error: Exception


@dataclass
class SetUserEngagementForNewsInfoCardRequest:
  userUUID: str
  newsInfoCardUUID: str
  engagementType: str


@dataclass_json
@dataclass
class SetUserEngagementForNewsInfoCardResponse:
  error: Exception

