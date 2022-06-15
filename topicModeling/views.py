from .serializers import *
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from .handler import *
from .handlerV2 import *
from idl import *

"""
  This file will handle the actual external facing API for the topicModeling service. This includes mapping all the httpRequest / httpResponse objects to internal dataclass objects and performing the necessary validation steps that are specified in the serializers class. If there are any issues in this mapping / validation it will return an error immediately.  This file is necessary since service to service will make calls to the handler based on the dataclass request/ response whereas the front end will make requests through http which needs to be serialized from the JSON struct that's passed in.
"""


@api_view(['GET'])
def retrain_topic_model_view(request):
  """
    This endpoint will first fetch all the documents from the database and keep it in memory
    It will then pass in the doc_ids and the document text to the topic model endpoint
    The topic model endpoint will then store the weights in a file that it will read during evaluation
  """
  res = retrain_topic_model()
  return Response(res.to_json())


@api_view(['POST'])
def add_document_view(request):
  """
    This endpoint will add a one off document to the topic model.  This endpoint takes in the article text, doc_ids if provided and adds the document to the topic model so that you can fetch the topic for the article in the future.
  """
  req = AddDocumentRequestSerializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  addDocumentRequest = req.validated_data
  res = add_document(addDocumentRequest)

  return Response(res.to_json())


@api_view(['POST'])
def query_documents_url_view(request):
  """
    This endpoint gets similar documents to a given document
  """
  req = QueryDocumentsRequestSerializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  queryDocumentsRequest = req.validated_data
  res = query_documents(queryDocumentsRequest)

  return Response(res.to_json())


@api_view(['POST'])
def search_documents_by_topic_view(request):
  """
    This endpoint will get the documents that are most related to a given topic id.
  """
  req = SearchDocumentsByTopicRequestSerializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  searchDocumentsByTopicRequest = req.validated_data
  res = search_documents_by_topic(searchDocumentsByTopicRequest)

  return Response(res.to_json())


@api_view(['POST'])
def search_topics_view(request):
  """
    This endpoint takes in a keyword and returns the top topics related to that keyword
  """
  req = SearchTopicsRequestSerializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  searchTopicsRequest = req.validated_data
  res = search_topics(searchTopicsRequest)

  return Response(res.to_json())


@api_view(['POST'])
def delete_topics_view(request):
  """
    This endpoint takes in a keyword and returns the top topics related to that keyword
  """
  req = DeleteTopicsRequestSerializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  deleteTopicsRequest = req.validated_data
  res = delete_topics(deleteTopicsRequest)

  return Response(res.to_json())


@api_view(['POST'])
def index_document_vectors_view(request):
  """
    This endpoint is responsible for re-indexing the documents after the topic model has been regenerated. In the case of individual articles being added to the topic model, it will be handled through add_document.
  """
  pass


@api_view(['GET'])
def generate_topic_pairs_view(request):
  """
    This endpoint will generate the topic pairs v2 for now to test out if it is better or not.  It better be though! At the very least it picks from a pre-determined list of topics so that should prove to be stronger than coming up with everything from scratch.
  """

  res = generate_topic_pairs_v2(request)
  print("FINISHED CALLING GENERATE TOPIC PAIRS V2")
  return Response()


@api_view(['POST'])
def get_document_topic_view(request):
  """
    This endpoint will query the topic model using the doc_ids, reduced, and num_topics parameters.
  """

  req = GetDocumentTopicRequestSerializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  getDocumentTopicRequest = req.validated_data
  res = get_document_topic(getDocumentTopicRequest)

  return Response(res.to_json())

###
#
# TopicModelingV2
#
###

@api_view(['GET'])
def retrain_topic_model_view_v2(request):
  """
    This endpoint will train both the Top2Vec model and BERTopic. It will store the generated topics in the topic database and
  """

  res = retrain_topic_model_v2(request)
  return Response(res.to_json())


@api_view(['POST'])
def get_document_topic_view_v2(request):
  """
    This will take in a list of documents and return the corresponding TopicInfo structs.
  """
  req = GetDocumentTopicRequestV2Serializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  getDocumentTopicRequestV2 = req.validated_data
  res = get_document_topic_v2(getDocumentTopicRequestV2)

  return Response(res.to_json())


@api_view(['GET'])
def get_topics_view_v2(request):
  """
    This endpoint will return all the topics that have been generated by the topic model.
  """
  res = get_topics_v2(request)
  return Response(res.to_json())


@api_view(['POST'])
def search_topics_view_v2(request):
  """
    This endpoint finds the topics most similar to a search term
  """
  req = SearchTopicsRequestV2Serializer(data=request.data)
  if not req.is_valid():
    return Response(req.errors)

  getTopicsRequestV2 = req.validated_data
  res = get_topics_v2(getTopicsRequestV2)

  return Response(res.to_json())

