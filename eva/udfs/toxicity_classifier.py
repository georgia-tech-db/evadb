# coding=utf-8
# Copyright 2018-2022 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import List

import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline

from eva.udfs.abstract.abstract_udf import AbstractClassifierUDF

class ToxicityClassifier(AbstractClassifierUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score
    """

    @property
    def name(self) -> str:
        return "ToxicityClassifier"

    def setup(self, threshold=0.3):
        self.threshold = threshold
        model_path = "s-nlp/roberta_toxicity_classifier"
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        mult_model_path = "EIStakovskii/xlm_roberta_base_multilingual_toxicity_classifier_plus"
        self.mult_tokenizer = AutoTokenizer.from_pretrained(mult_model_path)
        self.mult_model = AutoModelForSequenceClassification.from_pretrained(mult_model_path)



    @property
    def labels(self) -> List[str]:
        return ["toxic", "not toxic"]

    def forward(self, text_dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Performs predictions on input text
        Arguments:
            text (pd.DataFrame): Dataframe with text on which predictions need to be performed

            ['example text 1','example text 2']
            ['example text 3']
            ...
            ['example text 1','example text 5']

        Returns:
            outcome (List[Str])
        """
        # reconstruct dimension of the input
        outcome = pd.DataFrame()
        dataframe_size = text_dataframe.size

        for i in range(0, dataframe_size):
            text = text_dataframe.iat[i, 0]
            text = ' '.join(text)
            pipeline = TextClassificationPipeline(model = self.model, tokenizer = self.tokenizer)
            out = pipeline(text)

            multi_pipeline = TextClassificationPipeline(model=self.mult_model, tokenizer=self.mult_tokenizer)
            multi_out = multi_pipeline(text)

            out_label = out[0]['label']
            multi_out_label = multi_out[0]['label']
            multi_out_score = multi_out[0]['score']
            if out_label == 'toxic' or (multi_out_label == 'LABEL_1' and multi_out_score > self.threshold):
                outcome = pd.concat(
                    [outcome, pd.DataFrame({"labels": ["toxic"]})], ignore_index=True
                )
            else:
                outcome = pd.concat(
                    [outcome, pd.DataFrame({"labels": ["not toxic"]})],
                    ignore_index=True,
                )
        return outcome
