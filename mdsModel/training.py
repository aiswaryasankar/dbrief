"""
  This file will actually generate the MDS summary given the input articles.  It will use a t-5 model trained on the multiNews dataset.

"""

import logging
import os
import sys
from dataclasses import dataclass, field
from typing import Optional

import nltk  # Here to have a nice missing dependency error message early on
import numpy as np
from datasets import load_dataset, load_metric

# from . import transformers
from filelock import FileLock
import AutoConfig, AutoModelForSseq2SeqLM
from transformers import (
   AutoConfig,
   AutoModelForSeq2SeqLM,
   AutoTokenizer,
   HfArgumentParser,
)
from transformers.file_utils import is_offline_mode
from transformers.trainer_utils import get_last_checkpoint
from transformers.utils import check_min_version

model_path = ""
cache_dir = ""
model_revision = "0.0.1"
tokenizer_name = "t5-small"


def evaluate_mds():
  """
    This will evaluate the MDS model given the input text.
  """

  config = AutoConfig.from_pretrained(
    model_path,
    cache_dir=cache_dir,
    revision=model_revision,
    use_auth_token=None,
  )

  tokenizer = AutoTokenizer.from_pretrained(
    tokenizer_name,
    cache_dir = cache_dir,
    use_fast = False,
    revision = model_revision,
    use_auth_token = None,
  )

  model = AutoModelForSeq2SeqLM.from_pretrained(
    model_path,
    from_tf=True,
    config=config,
    cache_dir=cache_dir,
    revision=model_revision,
    use_auth_token=None,
  )







