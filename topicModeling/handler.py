import logging
import numpy as np
import pandas as pd
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import tempfile
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
from scipy.special import softmax
from sentence_transformers import SentenceTransformer
import logging
from topicModeling.training import Top2Vec
from rest_framework.decorators import api_view
from rest_framework.response import Response
import datetime
import idl
from idl import AddDocumentRequest, GetDocumentTopicResponse, QueryDocumentsRequest, QueryDocumentsResponse, GetDocumentTopicRequest

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@api_view(['GET'])
def retrain_topic_model(request):
  """
    This endpoint will first fetch all the documents from the database and keep it in memory
    It will then pass in the doc_ids and the document text to the topic model endpoint
    The topic model endpoint will then store the weights in a file that it will read during evaluation
  """

  # documents = ArticleModel.objects.all()
  # data = [doc.text for doc in documents]
  # doc_ids = [doc.articleId for doc in documents]

  startTime = datetime.datetime.now()
  model = Top2Vec(documents=data, speed="learn",embedding_model='universal-sentence-encoder', workers=4, document_ids=doc_ids)
  endTime = datetime.datetime.now()

  docIndex = Top2Vec.index_document_vectors(model)
  wordIndex = Top2Vec.index_word_vectors(model)
  savedModel = Top2Vec.save(self = model, file='./modelWeights/topicModelWeights')
  loadedModel = Top2Vec.load("./modelWeights/topicModelWeights")

  # logger.info("Time to train the topic2Vec model", endTime - startTime)
  return Response()

@api_view(['GET'])
def get_document_topic(GetDocumentTopicRequest):
  """
    This endpoint will query the topic model using the doc_ids, reduced, and num_topics parameters.
  """
  top2vecModel = Top2Vec.load("./modelWeights/topicModelWeights")
  res = top2vecModel.get_documents_topics(
    GetDocumentTopicRequest.doc_ids,
    GetDocumentTopicRequest.reduced,
    GetDocumentTopicRequest.num_topics,
  )
  return GetDocumentTopicResponse(
    topic_num = res.topic_num,
    topic_score = res.topic_score,
    topic_word = res.topic_word,
  )


@api_view(['GET'])
def add_document(AddDocumentRequest):
  """
    Req:
      documents: List of str
      doc_ids: List of str, int - this is the index that is stored in the mysql table
      tokenizer: optional
      use_embedding_model_tokenizer: optional
    Res:
      error

    Add a one off document to the topic model.  This endpoint takes in the article text, doc_ids if provided and adds the document to the topic model so that you can fetch the topic for the article in the future.
  """
  top2vecModel = Top2Vec.load("./modelWeights/topicModelWeights")
  res = top2vecModel.add_documents(AddDocumentRequest.documents, AddDocumentRequest.doc_ids)
  return idl.AddDocumentResponse(error=res)


@api_view(['GET'])
def query_documents_url(QueryDocumentsRequest):
  """
  Req: {
    Query: string - article body of text
    Num_docs: int - number of documents to return
    Return_documents: bool - will be false because we aren’t saving the documents in the model
    Use_index: bool - true by default because we want to use the index
    Ef: int - to experiment with but this leads to more accurate search > num docs
    Tokenizer: callable - tokenizer used throughout
  }
  Res: {
    Doc_scores: similarity scores of doc and vector
    Doc_ids: ids of the documents that are passed into the model
  }

    Gets the similar documents to a given document
  """
  top2vecModel = Top2Vec.load("./modelWeights/topicModelWeights")

  similarDocs = Top2Vec.query_documents(
    self=top2vecModel,
    query=QueryDocumentsRequest.query,
    num_docs=QueryDocumentsRequest.num_docs,
    return_documents=QueryDocumentsRequest.return_docs,
    use_index=QueryDocumentsRequest.use_index,
    ef=QueryDocumentsRequest.ef,
  )
  logger.info("Documents returned")
  logger.info(similarDocs)

  return QueryDocumentsResponse(
    doc_scores=similarDocs.doc_scores,
    doc_ids=similarDocs.doc_ids,
  )

def index_document_vectors(request):
  """
    This endpoint is responsible for re-indexing the documents after the topic model has been regenerated. In the case of individual articles being added to the topic model, it will be handled through add_document.
  """
  pass


