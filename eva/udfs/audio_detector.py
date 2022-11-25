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

class PhraseMatch(AbstractUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score
    """

    @property
    def name(self) -> str:
        return "phraseMatch"

    def setup(self, threshold=0.85):
        # Count something as a phrase only if there's < 0.5 sec difference between the end and the start of words
        self.word_gap_time_limit = 0.5
        self.threshold = threshold

    def forward(self, data: pd.DataFrame) -> pd.DataFrame:
        print(data)

        phrases = []

        # TODO: This should come from the query.
        phrase_length = 2

        # TODO: Change according to the repr of data.
        word_buffer = [data[0]]
        # TODO: Some attribute of data?
        for word_entry in data[1:]:

            # The new word was spoken close enough in time
            if int(word_entry["start_time"]) - int(word_buffer[-1]["end_time"]) <= self.word_gap_time_limit:
                word_buffer.append(word_entry)

                if len(word_buffer) == phrase_length:
                    phrases.append({
                        "start_time": word_buffer[0]["start_time"],
                        "end_time": word_buffer[-1]["end_time"],
                        "phrase": " ".join(buff_entry["word"] for buff_entry in word_buffer)}
                    )

                    # Trim away the first word in the buffer
                    word_buffer = word_buffer[1:]

            # The new world was spoken with a gap, reset the buffer.
            else:
                word_buffer = [word_entry]

        # Putting this in here to check what's returned
        phrases.append({"start_time": "", "end_time": "", "phrase": ""})
        return phrases