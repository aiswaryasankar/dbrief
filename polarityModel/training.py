import os
import math

import torch
from torch.nn import BCEWithLogitsLoss
from transformers import XLNetTokenizer, XLNetModel
from keras.preprocessing.sequence import pad_sequences
import numpy as np
import pandas as pd
import sentencepiece
import logging
from logtail import LogtailHandler

"""
  Define the classification model for evaluation.
"""

handler = LogtailHandler(source_token="tvoi6AuG8ieLux2PbHqdJSVR")
logger = logging.getLogger(__name__)
logger.handlers = [handler]
logger.setLevel(logging.INFO)

polarizationWeightsFile = "./modelWeights/xlnet_1.bin"
MAX_LEN = 512

class XLNetForPolarizationClassification(torch.nn.Module):

  def __init__(self, num_labels=2):
    """
      Initialize the model with the default config for XLNet
    """
    super(XLNetForPolarizationClassification, self).__init__()
    self.num_labels = num_labels
    self.xlnet = XLNetModel.from_pretrained('xlnet-base-cased')
    self.classifier = torch.nn.Linear(768, 1)
    torch.nn.init.xavier_normal_(self.classifier.weight)

  def forward(self, input_ids, token_type_ids=None, attention_mask=None, labels=None):
    """
      The architecture is xlnet + pooling layer + classifier + BCE
    """
    last_hidden_state = self.xlnet(input_ids=input_ids,
                                   attention_mask=attention_mask,
                                   token_type_ids=token_type_ids)
    mean_last_hidden_state = self.pool_hidden_state(last_hidden_state)
    logits = self.classifier(mean_last_hidden_state)

    # If you know the labels, compute the loss otherwise
    if labels is not None:
      loss_fct = BCEWithLogitsLoss() # 16, 8
      loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1, self.num_labels))
      return loss
    else:
      return logits


  def pool_hidden_state(self, last_hidden_state):
    """
      Pools the hidden state in the XLNet architecture
    """
    last_hidden_state = last_hidden_state[0]
    mean_last_hidden_state = torch.mean(last_hidden_state, 1)
    return mean_last_hidden_state



class XLNetPredict(torch.nn.Module):

  def __init__(self):
    """
      Initializes the prediction class for XLNet
    """
    super(XLNetPredict, self).__init__()
    self.tokenizer = XLNetTokenizer.from_pretrained('xlnet-base-cased', do_lower_case=True)
    self.model = XLNetForPolarizationClassification(2)

  def load_model(self, save_path):
    """
      Load the model from the path directory provided
    """
    # Load the model
    checkpoint = torch.load(save_path, map_location=torch.device('cpu'))
    model_state_dict = checkpoint['state_dict']
    model = XLNetForPolarizationClassification(num_labels=2)
    model.load_state_dict(model_state_dict)
    logger.info("Successfully loaded the polarization model")

    return model


  def predict(self, text):
    """
      Return the polarization score evaluated by the model
    """

    encoded_text = self.tokenizer.encode_plus(
      text,
      max_length=MAX_LEN,
      add_special_tokens=True,
      return_token_type_ids=False,
      pad_to_max_length=False,
      return_attention_mask=True,
      return_tensors='pt',
    )

    input_ids = pad_sequences(encoded_text['input_ids'], maxlen=MAX_LEN, dtype=torch.Tensor ,truncating="post",padding="post")
    input_ids = input_ids.astype(dtype = 'int64')
    input_ids = torch.tensor(input_ids)

    attention_mask = pad_sequences(encoded_text['attention_mask'], maxlen=MAX_LEN, dtype=torch.Tensor ,truncating="post",padding="post")
    attention_mask = attention_mask.astype(dtype = 'int64')
    attention_mask = torch.tensor(attention_mask)
    logger.info("Prepared the input for polarization model")

    input_ids = input_ids.reshape(1,512)
    attention_mask = attention_mask

    model = self.load_model(polarizationWeightsFile)

    outputs = model(input_ids=input_ids, attention_mask=attention_mask)
    logits = outputs.sigmoid().detach().cpu().numpy()
    logger.info("logits: ", logits)
    logger.info("rounded: ", round(logits[0][0]))

    return logits[0][0]


