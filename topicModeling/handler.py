import logging
import numpy as np
import pandas as pd
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sentence_transformers import SentenceTransformer
from logtail import LogtailHandler
from topicModeling.training import Top2Vec
from rest_framework.response import Response
from datetime import datetime
from idl import *
from articleRec import handler as articleRecHandler
from idl import *
from .repository import *
from django.conf import settings
import os
import tensorflow_hub as hub
from haystack.nodes import BM25Retriever, EmbeddingRetriever
from haystack.document_stores import ElasticsearchDocumentStore, FAISSDocumentStore


handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = []
logger.setLevel(logging.INFO)
logger.addHandler(handler)

embeddingModelPath = "./modelWeights/tfhub_cache"
if settings.TESTING:
  topicModelFile = "./modelWeights/topicModelWeights_test"
else:
  topicModelFile = "./modelWeights/topicModelWeights"


embedding_model = None

def retrain_topic_model():
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
  logger.info("Number of articles to index %s", len(articles))
  data = [article.text for article in articles]
  doc_ids = [article.id for article in articles]

  # train_bert_topic(data)

  startTime = datetime.now()
  model = Top2Vec(documents=data, speed="deep-learn", embedding_model='universal-sentence-encoder', workers=4, document_ids=doc_ids)
  endTime = datetime.now()

  docIndex = model.index_document_vectors()
  wordIndex = model.index_word_vectors()
  topicPairs, error = model.hierarchical_topic_reduction(num_topics=20)
  logger.info("topicPairs")
  logger.info(topicPairs)
  if error != None:
    return TrainAndIndexTopicModelResponse(
      error=ValueError("Failed to perform hierarchical topic reduction")
    )

  createTopicsResponse = createTopics(
    CreateTopicsRequest(
      topics=[TopicInfo(
        TopicID=None,
        TopicName=elem[0],
        ParentTopicName=elem[1],
      ) for elem in topicPairs]
    )
  )
  if createTopicsResponse.error != None:
    logger.info("Failed to store the topics in the database")

  parentTopics = model.get_topics(reduced=True)
  topics = model.get_topics(reduced=False)

  # Print out the topic hierarchy
  logger.info("Parent Topics")
  logger.info(parentTopics)
  logger.info("Topics")
  logger.info(topics)

  # Save and reload the model for validation purposes
  global embedding_model
  embedding_model = Top2Vec.save(self = model, file=topicModelFile)
  loadedModel = Top2Vec.load(topicModelFile)

  logger.info("Time to train the topic2Vec model", str(endTime - startTime))
  return TrainAndIndexTopicModelResponse(
    error=None,
  )


def get_document_topic_batch(getDocumentTopicBatchRequest):
  """
    This endpoint will return the topic and subtopic for a list of doc_ids.
  """
  top2vecModel = Top2Vec.load(topicModelFile)
  getDocumentTopicBatchResponse = top2vecModel.get_documents_topics(
    getDocumentTopicBatchRequest.doc_ids,
    getDocumentTopicBatchRequest.num_topics,
  )
  return getDocumentTopicBatchResponse


def get_document_topic(getDocumentTopicRequest):
  """
    This endpoint will query the topic model using the doc_ids, reduced, and num_topics parameters.
  """
  top2vecModel = Top2Vec.load(topicModelFile)
  getDocumentTopicRes = top2vecModel.get_documents_topics( # topic_num, topic_score, topic_word, _, error
    getDocumentTopicRequest.doc_ids,
    getDocumentTopicRequest.reduced,
    getDocumentTopicRequest.num_topics,
  )
  if getDocumentTopicRes.error != None:
    return GetDocumentTopicResponse(
      topic_num = None,
      topic_score = None,
      topic_word = None,
      error = getDocumentTopicRes.error,
    )

  return GetDocumentTopicResponse(
    topic_num = getDocumentTopicRes.topic_num,
    topic_score = getDocumentTopicRes.topic_score,
    topic_word = getDocumentTopicRes.topic_word,
    error = getDocumentTopicRes.error,
  )


def add_document(addDocumentRequest):
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
  global embedding_model
  if embedding_model == None:
    print("Embedding model is none in add document")
    embedding_model = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

  top2vecModel = Top2Vec.load(topicModelFile)
  err = top2vecModel.add_documents(addDocumentRequest.documents, addDocumentRequest.doc_ids, embedding_model=embedding_model)
  if err != None:
    return AddDocumentResponse(error=err)

  top2vecModel.save(topicModelFile)
  logger.info("Added %s documents to topic model", len(addDocumentRequest.doc_ids))
  return AddDocumentResponse(error=None)


def add_documents_faiss(addDocumentsFAISSRequest):
  """
    Adds documents to the FAISS index.
  """

  logger.info("Adding " + str(len(addDocumentsFAISSRequest.documents)) + " documents to FAISS")

  if not os.path.exists("./modelWeights/document_store"):
    document_store = FAISSDocumentStore(sql_url="sqlite:///modelWeights/haystack_test_faiss.db")
  else:
    document_store = FAISSDocumentStore.load(index_path="./modelWeights/document_store",
                                             config_path="./modelWeights/document_store.json")
  logger.info(f'Loaded document store')

  try:
    retriever = EmbeddingRetriever(document_store=document_store, embedding_model="deepset/sentence_bert", use_gpu=False)
    documents = addDocumentsFAISSRequest.documents

    document_store.write_documents(documents)
    document_store.update_embeddings(retriever)

    logger.info(f'Writing to document store done.')

    document_store.save("./modelWeights/document_store")

  except Exception as e:
    res = AddDocumentsFaissResponse(num_documents_added=None, error=e)
    return res

  return AddDocumentsFaissResponse(num_documents_added=len(documents), error=None)


def delete_documents_faiss(deleteDocumentsFAISSRequest):

  try:
    assert os.path.exists("./modelWeights/document_store")

    document_store = FAISSDocumentStore.load(index_path="./modelWeights/document_store",
                                             config_path="./modelWeights/document_store.json")

    logger.info(f'Document store loaded for deletion.')

    # TODO: some logic to check if we can delete and not actually delete

    article_ids = deleteDocumentsFAISSRequest.article_ids
    total_article_ids = len(article_ids)

    assert isinstance(article_ids,list) and len(article_ids)>0 and isinstance(article_ids[0],int)

    document_store.delete_documents(
      filters = {
        "id" : article_ids
      }
    )

    document_store.save("./modelWeights/document_store")

  except Exception as e:
    return DeleteDocumentsFAISSResponse(
      num_articles_deleted = 0,
      error = e
    )

  return DeleteDocumentsFAISSResponse(
    num_articles_deleted = total_article_ids,
    error = None
  )


def query_documents_faiss(queryDocumentsFAISSRequest):
  """
    Implement a document retriever using dense embeddings
  """

  if not os.path.exists("./modelWeights/document_store"):
    document_store = FAISSDocumentStore(sql_url="sqlite:///modelWeights/haystack_test_faiss.db")
  else:
    document_store = FAISSDocumentStore.load(index_path="./modelWeights/document_store",
                                             config_path="./modelWeights/document_store.json")
  logger.info(f'Loaded document store')

  retriever = EmbeddingRetriever(document_store=document_store,
                                 embedding_model="deepset/sentence_bert", use_gpu=False)

  logger.info(f'document store and retriever loaded.')

  candidate_documents = retriever.retrieve(
      query=queryDocumentsFAISSRequest.query,
      top_k=queryDocumentsFAISSRequest.num_docs,
  )

  logger.info("Faiss Retriever docs" + str(candidate_documents))
  return QueryDocumentsFaissResponse (
    candidate_documents = candidate_documents,
    error=None,
  )


def add_documents_elastic_search(addElasticSearchDocumentRequest):
  """
    Will add all documents to Elastic Search in batch. This is used essentially to entirely refresh the index of articles in the database.
  """

  logger.info("Adding " + str(len(addElasticSearchDocumentRequest.documents)) + " documents to elastic search")

  try:
    document_store = ElasticsearchDocumentStore(host="localhost", username="", password="", index="document")
    documents = addElasticSearchDocumentRequest.documents
    document_store.write_documents(documents)

    logger.info(f'Successfully wrote ' + str(len(addElasticSearchDocumentRequest.documents) + " to elastic search"))

  except Exception as e:
    res = AddDocumentsElasticSearchResponse(num_documents_added=None, error=e)
    return res

  return AddDocumentsElasticSearchResponse(num_documents_added=len(documents), error=None)


def delete_documents_elastic_search(deleteDocumentsElasticSearchRequest):
  """
    Delete article IDs from elastic search.
  """

  try:
    document_store = ElasticsearchDocumentStore(host="localhost", username="", password="", index="document")

    logger.info(f'Document store loaded for deletion.')

    article_ids = deleteDocumentsElasticSearchRequest.article_ids
    total_article_ids = len(article_ids)

    assert isinstance(article_ids,list) and len(article_ids)>0 and isinstance(article_ids[0],int)

    document_store.delete_documents(
      filters = {
        "id" : article_ids
      }
    )

  except Exception as e:
    return DeleteDocumentsElasticSearchResponse(
      num_articles_deleted = 0,
      error = e
    )

  return DeleteDocumentsElasticSearchResponse(
    num_articles_deleted = total_article_ids,
    error = None
  )


def query_documents_elastic_search(queryDocumentsRequest):
  """
    Implement a BM25 retriever for elastic search retrieval
  """
  document_store = ElasticsearchDocumentStore(host="localhost", username="", password="", index="document")
  retriever = BM25Retriever(document_store)

  candidate_documents = retriever.retrieve(
      query=queryDocumentsRequest.query,
      top_k=queryDocumentsRequest.num_docs,
  )

  logger.info("BM25 Retriever docs" + str(candidate_documents))
  return QueryDocumentsElasticSearchResponse(
    candidate_documents=candidate_documents,
    error=None,
  )


def query_documents(queryDocumentsRequest):
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
  global embedding_model
  if embedding_model == None:
    print("Embedding model is none in query documents")
    embedding_model = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

  top2vecModel = Top2Vec.load(topicModelFile)

  _, doc_scores, doc_ids, error = Top2Vec.query_documents(
    self=top2vecModel,
    query=queryDocumentsRequest.query,
    num_docs=queryDocumentsRequest.num_docs,
    return_documents=queryDocumentsRequest.return_docs,
    use_index=queryDocumentsRequest.use_index,
    ef=queryDocumentsRequest.ef,
    embedding_model = embedding_model,
  )
  if doc_scores == [] or doc_ids == [] or error != None:
    return QueryDocumentsResponse(
      doc_scores=doc_scores,
      doc_ids=doc_ids,
      error=ValueError("No documents returned by search"),
    )

  # Retrieve docs from the db
  hnswlib_urls = []
  fetchArticlesRes = articleRecHandler.fetch_articles(
    FetchArticlesRequest(
      articleIds=doc_ids,
    )
  )
  if fetchArticlesRes.error != None:
    logger.warn("Failed to fetch doc id from mysql")
  else:
    hnswlib_urls = [article.url for article in fetchArticlesRes.articleList]

  logger.info("Documents returned HNSWlib", extra={
    'doc_ids': doc_ids,
    'doc_scores': doc_scores,
  })
  logger.info(doc_ids)
  logger.info(doc_scores)
  logger.info("HNSWLIB urls: " + str(hnswlib_urls))

  # Query docs from FAISS and log the results for offline evaluation purposes
  queryDocumentsFaissRes = query_documents_faiss(
    QueryDocumentsFaissRequest (
      query=queryDocumentsRequest.query,
      num_docs=queryDocumentsRequest.num_docs,
    )
  )
  if queryDocumentsFaissRes.error != None:
    logger.warn("Failed to query documents through FAISS: " + str(queryDocumentsFaissRes.error))
  else:
    faiss_urls = [doc.meta['url'] for doc in queryDocumentsFaissRes.candidate_documents]
    logger.info("Documents returned FAISS")
    logger.info(faiss_urls)

  # Query docs from Elastic Search and log results for eval
  queryDocumentsElasticSearchRes = query_documents_elastic_search(
    queryDocumentsRequest= QueryDocumentsElasticSearchRequest (
      query=queryDocumentsRequest.query,
      num_docs=queryDocumentsRequest.num_docs,
    )
  )
  if queryDocumentsElasticSearchRes.error != None:
    logger.warn("Failed to query documents through Elastic Search: " + str(queryDocumentsElasticSearchRes.error))
  else:
    es_urls = [doc.meta['url'] for doc in queryDocumentsElasticSearchRes.candidate_documents]
    logger.info("Documents returned Elastic Search")
    logger.info("documents: " + str(queryDocumentsElasticSearchRes.candidate_documents))
    logger.info(es_urls)

  # Create thread to compute the ROUGE, tf-idf and overlap scores btwn the 3 different indices
  # Log statement with all of the scores

  return QueryDocumentsResponse(
    elastic_search_urls = es_urls,
    faiss_urls = faiss_urls,
    hnswlib_urls = hnswlib_urls,
    doc_scores=[float(score) for score in doc_scores],
    doc_ids=[float(doc_id) for doc_id in doc_ids],
    error=None,
  )


def index_document_vectors(request):
  """
    This endpoint is responsible for re-indexing the documents after the topic model has been regenerated. In the case of individual articles being added to the topic model, it will be handled through add_document.
  """
  pass


def generate_topic_pairs():
  """
    This endpoint will generate the topic<>parentTopic pairs given the hierarchy of topics in the topic model. It will be returned as a list of lists with [topic, parentTopic]
  """
  top2vecModel = Top2Vec.load(topicModelFile)
  topicPairs = top2vecModel.generate_topic_parent_topic_pairs()
  logger.info("topic pairs")
  logger.info(topicPairs)
  return GenerateTopicPairsResponse(
    topic_pairs=topicPairs
  )


def generate_topic_pairs_v2(request):
  """
    This endpoint smartly chooses the best parent topic for a given child topic word.
  """
  global embedding_model
  if embedding_model == None:
    print("Embedding model is none in query documents")
    embedding_model = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

  top2vecModel = Top2Vec.load(topicModelFile)
  topicPairs = top2vecModel.generate_topic_parent_topic_pairs_v2(embedding_model)
  return GenerateTopicPairsResponse(
    topic_pairs=topicPairs,
  )


def search_documents_by_topic(searchDocumentsByTopic):
  """
    This endpoint will get the documents that are most related to a given topic id.
  """

  top2vecModel = Top2Vec.load(topicModelFile)
  _, doc_scores, doc_ids, error = top2vecModel.search_documents_by_topic(
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
    error=error,
  )


def search_topics(searchTopicsRequest):
  """
    This endpoint takes in a keyword and returns the top topics related to that keyword
  """

  top2vecModel = Top2Vec.load(topicModelFile)
  topic_words, _, topic_scores, topic_nums, error = top2vecModel.search_topics(searchTopicsRequest.keywords, searchTopicsRequest.num_topics)

  if error != None:
    return SearchTopicsResponse(
      topics_words=topic_words,
      topic_scores=topic_scores,
      topic_nums=topic_nums,
      error=error,
    )

  logger.info("Top topics for keyword")
  logger.info(searchTopicsRequest.keywords)
  logger.info("topic_words")
  logger.info([words[0] for words in topic_words])
  logger.info("topic_nums")
  logger.info(topic_nums)
  logger.info(topic_scores)

  fetchTopicInfosBatchRes = fetch_topic_infos_batch(
    FetchTopicInfoBatchRequest(
      topicNames=[words[0] for words in topic_words],
    )
  )
  if fetchTopicInfosBatchRes.error != None:
    logger.info("Failed to fetch topic infos batch")

  return SearchTopicsResponse(
    topics_words=[words[0] for words in topic_words],
    topic_scores=None,
    topic_nums=None,
    topic_infos=fetchTopicInfosBatchRes.topics,
    error=None
  )


def get_topics(getTopicsRequest):
  """
    This endpoint will get the top x topics listed by size and return the topic word and topic number associated with the topic
  """
  top2vecModel = Top2Vec.load(topicModelFile)
  topic_words, _, topic_nums, error = top2vecModel.get_topics(
    num_topics=getTopicsRequest.num_topics,
    reduced = getTopicsRequest.reduced,
  )
  return GetTopicsResponse(
    topic_words=topic_words,
    topic_nums=topic_nums,
    error=error,
  )


def fetch_topic_infos_batch(fetchTopicInfoBatchRequest):
  """
    Given a list of topicIds this endpoint will return hydrated topicInfo entities
  """
  fetchTopicInfoBatchResponse = fetchTopicInfoBatch(fetchTopicInfoBatchRequest)

  return fetchTopicInfoBatchResponse


def fetch_random_topic_info_batch():
  """
    Fetch random set of topics guaranteed to be in the database.
  """
  fetchTopicInfoBatchResponse = fetchRandomTopicInfoBatch()

  return fetchTopicInfoBatchResponse


def delete_documents_batch(deleteDocumentsRequest):
  """
    This endpoint will remove documents from the topic model after they have been removed from the mysql table
  """
  top2vecModel = Top2Vec.load(topicModelFile)
  num_articles_deleted, err = top2vecModel.delete_documents(
    doc_ids = deleteDocumentsRequest.docIds,
  )
  if err != None:
    logger.info("Failed to delete %s documents", len(deleteDocumentsRequest.docIds))
    logger.warn(err)

    return DeleteDocumentsResponse(
      numArticlesDeleted=0,
      error=err,
    )

  return DeleteDocumentsResponse(
    numArticlesDeleted=num_articles_deleted,
    error=None,
  )


def delete_topics(deleteTopicsRequest):
  """
    This endpoint will delete old topics to maintain topic freshness for all users.
  """
  deleteTopicsByTimeRangeRes = deleteTopicsByTimeRange(
    DeleteArticlesRequest(
      num_days = deleteTopicsRequest.num_days,
    )
  )
  if deleteTopicsByTimeRangeRes.error != None:
    return deleteTopicsByTimeRangeRes

  return deleteTopicsByTimeRangeRes


def fetch_all_topics():
  """
    Fetch all the topics for the database.
  """
  return fetchAllTopics()

