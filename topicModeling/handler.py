import logging
import numpy as np
import pandas as pd
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sentence_transformers import SentenceTransformer
from logtail import LogtailHandler
from topicModeling.training import Top2Vec
from rest_framework.response import Response
import datetime
from idl import *
from articleRec import handler as articleRecHandler
from idl import AddDocumentRequest, GetDocumentTopicResponse, QueryDocumentsRequest, QueryDocumentsResponse, GetDocumentTopicRequest

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)

topicModelFile = "./modelWeights/topicModelWeights"


def retrain_topic_model(request):
  """
    This endpoint will first fetch all the documents from the database and keep it in memory
    It will then pass in the doc_ids and the document text to the topic model endpoint
    The topic model endpoint will then store the weights in a file that it will read during evaluation. Finally it will call the topic model to perform hierarchical topic reduction in order to get the topics and the sub topics as well.
  """

  fetchAllArticlesResponse = articleRecHandler.fetch_articles(
    FetchArticlesRequest(articleIds=[])
  )
  if fetchAllArticlesResponse.error != None:
    return TrainAndIndexTopicModelResponse(
      error=ValueError(fetchAllArticlesResponse.error, "Failed to fetch articles from the articleRec db")
    )

  articles = fetchAllArticlesResponse.articleList
  logger.info("Fetched all articles from the db")
  logger.info(len(articles))
  data = [article.text for article in articles]
  doc_ids = [article.id for article in articles]

  startTime = datetime.datetime.now()
  model = Top2Vec(documents=data, speed="learn",embedding_model='universal-sentence-encoder', workers=4, document_ids=doc_ids)
  endTime = datetime.datetime.now()

  docIndex = Top2Vec.index_document_vectors(model)
  wordIndex = Top2Vec.index_word_vectors(model)
  topicReduction = model.hierarchical_topic_reduction(num_topics=20)
  parentTopics = model.get_topics(reduced=True)
  topics = model.get_topics(reduced=False)

  # Print out the topic hierarchy
  logger.info("Parent Topics")
  logger.info(parentTopics)
  logger.info("Topics")
  logger.info(topics)

  # Save and reload the model for validation purposes
  savedModel = Top2Vec.save(self = model, file=topicModelFile)
  loadedModel = Top2Vec.load(topicModelFile)

  # logger.info("Time to train the topic2Vec model", endTime - startTime)
  return TrainAndIndexTopicModelResponse(
    error=None,
  )


def get_document_topic(GetDocumentTopicRequest):
  """
    This endpoint will query the topic model using the doc_ids, reduced, and num_topics parameters.
  """
  top2vecModel = Top2Vec.load(topicModelFile)
  topic_num, topic_score, topic_word, _, error = top2vecModel.get_documents_topics(
    GetDocumentTopicRequest.doc_ids,
    GetDocumentTopicRequest.reduced,
    GetDocumentTopicRequest.num_topics,
  )
  return GetDocumentTopicResponse(
    topic_num = topic_num,
    topic_score = topic_score,
    topic_word = topic_word,
    error = error,
  )


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
  top2vecModel = Top2Vec.load(topicModelFile)
  err = top2vecModel.add_documents(AddDocumentRequest.documents, AddDocumentRequest.doc_ids)
  if err != None:
    return AddDocumentResponse(error=err)

  top2vecModel.save(topicModelFile)
  return AddDocumentResponse(error=None)


def query_documents_url(queryDocumentsRequest):
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
  top2vecModel = Top2Vec.load(topicModelFile)

  doc_scores, doc_ids = Top2Vec.query_documents(
    self=top2vecModel,
    query=queryDocumentsRequest.query,
    num_docs=queryDocumentsRequest.num_docs,
    return_documents=queryDocumentsRequest.return_docs,
    use_index=queryDocumentsRequest.use_index,
    ef=queryDocumentsRequest.ef,
  )
  logger.info("Documents returned")
  logger.info(doc_ids)

  if doc_scores == [] or doc_ids == []:
    return QueryDocumentsResponse(
      doc_scores=doc_scores,
      doc_ids=doc_ids,
      error=ValueError("No documents returned by search"),
    )

  return QueryDocumentsResponse(
    doc_scores=doc_scores,
    doc_ids=doc_ids,
    error=None,
  )


def index_document_vectors(request):
  """
    This endpoint is responsible for re-indexing the documents after the topic model has been regenerated. In the case of individual articles being added to the topic model, it will be handled through add_document.
  """
  pass


def search_documents_by_topic(searchDocumentsByTopic):
  """
    This endpoint will get the documents that are most related to a given topic id.
  """

  top2vecModel = Top2Vec.load(topicModelFile)
  doc_scores, doc_ids = top2vecModel.search_documents_by_topic(
    searchDocumentsByTopic.topic_num,
    searchDocumentsByTopic.num_docs,
    False,
    False,
  )
  logger.info("Doc scores")
  logger.info(doc_scores)
  logger.info(doc_ids)


  return SearchDocumentsByTopicResponse(
    doc_ids=doc_ids,
    doc_scores=doc_scores,
  )


def search_topics(searchTopicsRequest):
  """
    This endpoint takes in a keyword and returns the top topics related to that keyword
  """
  top2vecModel = Top2Vec.load(topicModelFile)
  topic_words, _, topic_scores, topic_nums = top2vecModel.search_topics(searchTopicsRequest.keywords, searchTopicsRequest.num_topics)

  logger.info("Top topics for keyword")
  logger.info(searchTopicsRequest.keywords)
  logger.info("topic_words")
  logger.info(topic_words)
  logger.info("topic_nums")
  logger.info(topic_nums)
  logger.info(topic_scores)

  return SearchTopicsResponse(
    topics_words=topic_words,
    topic_scores=topic_scores,
    topic_nums=topic_nums,
  )

