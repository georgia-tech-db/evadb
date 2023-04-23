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
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from eva.udfs.abstract.abstract_udf import AbstractClassifierUDF

DOWNLOAD_URL = "https://github.com/unitaryai/detoxify/releases/download/"
MODEL_URLS = {
    "original": DOWNLOAD_URL + "v0.1-alpha/toxic_original-c1212f89.ckpt",
    "unbiased": DOWNLOAD_URL + "v0.3-alpha/toxic_debiased-c7548aa0.ckpt",
    "multilingual": DOWNLOAD_URL + "v0.4-alpha/multilingual_debiased-0b549669.ckpt",
    "original-small": DOWNLOAD_URL + "v0.1.2/original-albert-0e1d6498.ckpt",
    "unbiased-small": DOWNLOAD_URL + "v0.1.2/unbiased-albert-c8519128.ckpt",
}


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
        self.model_type2id = {
            "original": "unitary/toxic-bert",
            "unbiased": "unitary/unbiased-toxic-roberta",
            "multilingual": "unitary/multilingual-toxic-xlm-roberta",
        }
        self.change_names = {
            "toxic": "toxicity",
            "identity_hate": "identity_attack",
            "severe_toxic": "severe_toxicity",
        }

    # create udf -> search for query
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
            sum_toxicity_score = 0
            for model_type in self.model_type2id:
                model_id = self.model_type2id[model_type]
                tokenizer = AutoTokenizer.from_pretrained(model_id)
                model = AutoModelForSequenceClassification.from_pretrained(model_id)
                checkpoint_path = MODEL_URLS[model_type]
                loaded = torch.hub.load_state_dict_from_url(checkpoint_path)
                class_names = loaded["config"]["dataset"]["args"]["classes"]
                class_names = [self.change_names.get(cl, cl) for cl in class_names]

                input = tokenizer(
                    text, return_tensors="pt", truncation=True, padding=True
                )
                out = model(**input)[0]
                scores = torch.sigmoid(out).cpu().detach().numpy()
                single_result = {}
                if model_type == "multilingual":
                    class_names = ["toxicity"]
                for i, cla in enumerate(class_names):
                    single_result[cla] = (
                        scores[0][i]
                        if isinstance(text, str)
                        else [scores[ex_i][i].tolist() for ex_i in range(len(scores))]
                    )

                toxicity_score = single_result["toxicity"][0]
                print("\nModel: ", model_type, " toxicity_score: ", toxicity_score)
                sum_toxicity_score += toxicity_score

            avg_toxicity_score = sum_toxicity_score / len(self.model_type2id)
            print("\n final average toxicity score: ", avg_toxicity_score)
            if avg_toxicity_score >= self.threshold:
                outcome = pd.concat(
                    [outcome, pd.DataFrame({"labels": ["toxic"]})], ignore_index=True
                )
            else:
                outcome = pd.concat(
                    [outcome, pd.DataFrame({"labels": ["not toxic"]})],
                    ignore_index=True,
                )
        print("final outcome: ", outcome)
        return outcome
