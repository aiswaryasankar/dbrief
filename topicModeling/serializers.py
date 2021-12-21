from rest_framework import serializers
from idl import *
from rest_framework_dataclasses.serializers import DataclassSerializer

"""
  This file will define all the Serializers for the topicModeling service.  Serializers serve to map and handle validation between httpRequest objects passed into the service and the dataclasses used to store and pass data around internally between the various apps.
"""

class SearchDocumentsByTopicRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = SearchDocumentsByTopicRequest

class SearchTopicsRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = SearchTopicsRequest

class AddDocumentRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = AddDocumentRequest

class QueryDocumentsRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = QueryDocumentsRequest

class TrainAndIndexTopicModelRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = TrainAndIndexTopicModelRequest

class QueryDocumentsRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = QueryDocumentsRequest

class GetDocumentTopicRequestSerializer(DataclassSerializer):
  class Meta:
    dataclass = GetDocumentTopicRequest


# @dataclass
# class SearchDocumentsByTopicResponse:
#   doc_ids: List[int]
#   doc_scores: List[int]
#   error: Optional[Exception]

# @dataclass
# class SearchTopicsResponse:
#   topics_words: List[str]
#   topic_scores: List[float]
#   topic_nums: List[int]

# @dataclass
# class AddDocumentResponse:
#   error: Exception

# @dataclass
# class QueryDocumentsResponse:
#   doc_scores: List[int]
#   doc_ids: List[int]
#   error: Exception

# @dataclass
# class TrainAndIndexTopicModelResponse:
#   error: Exception

# @dataclass
# class QueryDocumentsResponse:
#   doc_scores: List[int]
#   doc_ids: List[int]
#   error: Exception

# @dataclass
# class GetDocumentTopicResponse:
#   topic_num: int
#   topic_score: float
#   topic_word: str
#   error: Exception