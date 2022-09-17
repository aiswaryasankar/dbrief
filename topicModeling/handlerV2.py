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
from idl import *
from .repository import *
from topicModeling.trainingV2 import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from django.conf import settings



handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)

if settings.TESTING:
  topicModelFile = "./modelWeights/BERTopicWeights_test"
  articleIndexFile  = "./modelWeights/Top2VecWeights_test"
else:
  topicModelFile = "./modelWeights/BERTopicWeights"
  articleIndexFile  = "./modelWeights/Top2VecWeights"


def train_bert_topic(docs):
  """
    Comparing the topics generated through BERTopic with the ones generated through Top2Vec
  """
  vectorizer_model = CountVectorizer(ngram_range=(1, 2), stop_words="english")
  topic_model = BERTopic(
    vectorizer_model=vectorizer_model,
    min_topic_size=20,
    calculate_probabilities=True,
    ).fit(docs)
  topics, probs = topic_model.fit_transform(docs)
  logger.info(topics)
  logger.info(probs)
  logger.info("BERTopic topics")
  df = topic_model.get_topic_info()

  for _, row in df.iterrows():
    logger.info(row)


def retrain_topic_model_v2(request):
  """
    This endpoint will first fetch all the documents from the database and keep it in memory
    It will then pass in the doc_ids and the document text to the topic model endpoint
    The topic model endpoint will then store the weights in a file that it will read during evaluation. Finally it will call the topic model to perform hierarchical topic reduction in order to get the topics and the sub topics as well.
  """

  # Fetch all articles from the database
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

  # Train Top2Vec
  startTime = datetime.now()
  model = Top2Vec(documents=data, speed="deep-learn", embedding_model='universal-sentence-encoder', workers=4, document_ids=doc_ids)
  endTime = datetime.now()

  docIndex = Top2Vec.index_document_vectors(model)
  wordIndex = Top2Vec.index_word_vectors(model)

  savedArticleModel = Top2Vec.save(self = model, file=articleIndexFile)
  loadedArticleModel = Top2Vec.load(articleIndexFile)


  # Train BERTopic
  vectorizer_model = CountVectorizer(ngram_range=(1, 2), stop_words="english")
  topic_model = BERTopic(
    vectorizer_model=vectorizer_model,
    min_topic_size=20,
    calculate_probabilities=True,
    ).fit(data)

  _, _ = topic_model.fit_transform(data)

  logger.info("BERTopic topics")
  df = topic_model.get_topic_info()

  createTopicsResponse = createTopics(
    CreateTopicsRequest(
      topics=[TopicInfo(
        TopicID=None,
        TopicName=row["Name"].split("_")[1],
        ParentTopicName=row["Name"].split("_")[2],
      ) for _, row in df.iterrows()]
    )
  )
  if createTopicsResponse.error != None:
    logger.info("Failed to store the topics in the database")

  # Print out the topic hierarchy
  logger.info("Topics")
  logger.info([row["Name"].split("_")[1] for _, row in df.iterrows()])
  logger.info("Parent Topics")
  logger.info([row["Name"].split("_")[2] for _, row in df.iterrows()])

  # Save the topic model
  savedTopicModel = topic_model.save(path=topicModelFile)
  loadedTopicModel = topic_model.load(path=topicModelFile)

  return TrainAndIndexTopicModelResponse(
    error=None,
  )


def get_document_topic_v2(getDocumentTopicV2Request):
  """
    This will take in a list of documents and return the corresponding TopicInfo structs.

      class GetDocumentTopicRequestV2:
        documents: List[str]

      class GetDocumentTopicResponseV2:
        topicInfos: List[TopicInfo]
        error: Exception

  """

  topicModel = BERTopic.load(topicModelFile)
  predictions, _ = topicModel.transform(getDocumentTopicV2Request.documents)

  topicList = []
  for prediction in predictions:
    topicPred = topicModel.get_topic(prediction[0])
    # In the future instead of choosing the first word returned in the topic words,
    # run this through the topic rule list and select the appropriate topic word
    topicList.append(topicPred[0][0])

  # Fetch the corresponding topic from the topic database
  fetchTopicInfoBatchResponse = fetchTopicInfoBatch(
    FetchTopicInfoBatchRequest(
      topicNames=topicList,
    )
  )
  if fetchTopicInfoBatchResponse.error != None:
    return GetDocumentTopicResponseV2(
      topicInfos=None,
      error = fetchTopicInfoBatchResponse.error,
    )

  return GetDocumentTopicResponseV2(
    topicInfos=fetchTopicInfoBatchResponse.topics,
    error = None,
  )


def search_topics_v2(searchTopicsV2Request):
  """
    Finds the topics most similar to a search term
  """
  topicModel = BERTopic.load(topicModelFile)

  # This returns topics as a tuple of ([topicIds], [scores]) will only need the topicIds
  similar_topics = topicModel.find_topics(
    searchTopicsV2Request.search_term,
    searchTopicsV2Request.num_topics,
  )

  topicIds = similar_topics[0]
  topicList = []
  for topicId in topicIds:
    topicPred = topicModel.get_topic(topicId)
    # In the future instead of choosing the first word returned in the topic words,
    # run this through the topic rule list and select the appropriate topic word
    topicList.append(topicPred[0][0])

  # Fetch the corresponding topic from the topic database
  fetchTopicInfoBatchResponse = fetchTopicInfoBatch(
    FetchTopicInfoBatchRequest(
      topicNames=topicList,
    )
  )
  if fetchTopicInfoBatchResponse.error != None:
    return SearchTopicsResponseV2(
      topicInfos=None,
      error = fetchTopicInfoBatchResponse.error,
    )

  return SearchTopicsResponseV2(
      topicInfos=fetchTopicInfoBatchResponse.topics,
      error = None,
    )


# def generate_topic_pairs_v2(generateTopicPairsV2Request):
#   """
#     Generate the topic<>parentTopic pairs given the hierarchy of topics in the topic model. Either use the reduce_topics function or run through the classification model for the parent topic.
#   """
#   # Can be implemented later, not a core endpoint
#   pass


def search_documents_by_topic_v2(searchDocumentsByTopicV2Request):
  """
    get the documents that are most related to a given topicId
  """
  # Currently only used in WhatsHappening
  pass


def get_topics_v2(getTopicsV2Request):
  """
    This will return all the topics that have been generated by the topic model. Since this is only used internally by WhatsHappening, it isn't key feature for now.
  """
  topicModel = BERTopic.load(topicModelFile)

  # This returns topics as a tuple of ([topicIds], [scores]) will only need the topicIds
  all_topics = topicModel.get_topics()
  logger.info("All topics")
  logger.info(all_topics)

  topicList = [all_topics[topicId][0][0] for topicId in all_topics]
  logger.info("Topic list")
  logger.info(topicList)

  # Fetch the corresponding topic from the topic database
  fetchTopicInfoBatchResponse = fetchTopicInfoBatch(
    FetchTopicInfoBatchRequest(
      topicNames=topicList,
    )
  )
  if fetchTopicInfoBatchResponse.error != None:
    return GetTopicsResponseV2(
      topicInfos=None,
      error = fetchTopicInfoBatchResponse.error,
    )

  return GetTopicsResponseV2(
      topicInfos=fetchTopicInfoBatchResponse.topics,
      error = None,
    )


def topic_rule_engine(topicRuleEngineRequest):
  """
    Given a list of the top 5 words for all possible topics, this will apply the following rules and select the best word to represent each topic.

      1. Don't allow acronyms
      2. Don't allow duplicate topic names
      3. Don't allow verbs
      4. Don't allow acronyms
  """
  pass






