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

import pandas as pd

from eva.udfs.abstract.abstract_udf import AbstractUDF

class Phrases(AbstractUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score
    """

    @property
    def name(self) -> str:
        return "phraseMatch"

    def setup(self, threshold=0.85, word_gap_time_limit=0.5):
        # Count something as a phrase only if there's < 0.5 sec difference between the end and the start of words
        self.word_gap_time_limit = word_gap_time_limit
        self.threshold = threshold
        self.prop_idx = {
            "WORD": 3,
            "START": 4,
            "END": 5
        }

    def forward(self, data: pd.DataFrame) -> pd.DataFrame:
        phrases = pd.DataFrame()

        first_row = data.iloc[0].values.tolist()
        phrase_length = first_row[-1]

        word_buffer = [{
            "word": first_row[self.prop_idx["WORD"]],
            "start_time": float(first_row[self.prop_idx["START"]]),
            "end_time": float(first_row[self.prop_idx["END"]])
        }]

        first = True
        for _, row_df in data.iterrows():
            if first:
                first = False
                continue

            row = row_df.values.tolist()
            word_entry = {
                "word": row[self.prop_idx["WORD"]],
                "start_time": float(row[self.prop_idx["START"]]),
                "end_time": float(row[self.prop_idx["END"]])
            }

            if phrase_length == 1:
                word_entry["phrase"] = word_entry["word"]
                del word_entry["word"]
                phrases = pd.concat([phrases, pd.DataFrame([word_entry])])
                continue

            # The new word was spoken close enough in time
            if word_entry["start_time"] - word_buffer[-1]["end_time"] <= self.word_gap_time_limit:
                word_buffer.append(word_entry)

                if len(word_buffer) == phrase_length:
                    phrases = pd.concat([
                        phrases,
                        pd.DataFrame([
                            {
                                "phrase": " ".join(buff_entry["word"] for buff_entry in word_buffer),
                                "start_time": word_buffer[0]["start_time"],
                                "end_time": word_buffer[-1]["end_time"]
                            }
                        ])
                    ])

                    # Trim away the first word in the buffer
                    word_buffer = word_buffer[1:]

            # The new world was spoken with a gap, reset the buffer.
            else:
                word_buffer = [word_entry]

        return phrases
