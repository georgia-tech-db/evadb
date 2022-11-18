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

import numpy as np
import pandas as pd

from eva.udfs.abstract.abstract_udf import AbstractUDF
from eva.utils.audio_utils import *

class WordMatch(AbstractUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score
    """

    @property
    def name(self) -> str:
        return "wordMatch"

    def setup(self, threshold=0.85):
        self.threshold = threshold

    def forward(self, args: pd.DataFrame) -> pd.DataFrame:
        table_name = args[args.columns[0]][0]
        target_word = args[args.columns[-1]][0]

        print(f"Tbl: ${table_name}, Word: ${target_word}")

        outcome = pd.DataFrame()

        # TODO: Get this from audio_utils
        video_word_list = []

        for word in video_word_list:
            pass
            # TODO: Replace this with something more sensible
            # outcome = outcome.append(
            #     {"labels": pred_class, "scores": pred_score, "bboxes": pred_boxes},
            #     ignore_index=True,
            # )

        # Putting this in here to check what's returned
        outcome.append({"time_region": np.array(["test-start", "test-end"])})
        return outcome