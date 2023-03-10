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

import re
import string

import numpy as np
import pandas as pd
import torch

from eva.udfs.abstract.abstract_udf import AbstractUDF

try:
    import whisper
except ImportError as e:
    raise ImportError(
        f"Failed to import with error {e}, \
        please try `pip install openai-whisper`"
    )


class AudioSearch(AbstractUDF):
    @property
    def name(self) -> str:
        return "AudioSearch"

    def setup(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = whisper.load_model("base", device=self.device)
        self.segment_window = 1
        self.segment_overlap = 1

    def forward(self, data: pd.DataFrame) -> pd.DataFrame:
        # join all the individual audio segments
        audio_segments = np.concatenate(data.iloc[:, 0])
        # string translator for removing punctuation
        punctuation_translator = str.maketrans("", "", string.punctuation)
        phrase = (
            data.iloc[0].values[1].translate(punctuation_translator).lower().strip()
        )

        # get text segments from video using whisper
        segments = []
        result = self.model.transcribe(audio_segments, fp16=torch.cuda.is_available())
        for segment in result["segments"]:
            segments.append(
                {
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"]
                    .translate(punctuation_translator)
                    .lower()
                    .strip(),
                }
            )

        # do a rolling merge of the text segments, as the search phrase may extend over multiple segments
        merged = []
        for first in range(0, len(segments), self.segment_overlap):
            last = min(len(segments) - 1, first + self.segment_window - 1)
            text = " ".join(segment["text"] for segment in segments[first : last + 1])
            merged.append(
                {
                    "start": segments[first]["start"],
                    "end": segments[last]["end"],
                    "text": text,
                }
            )

        del segments
        # TODO: cache merged text segments

        last_found = -1
        output = pd.DataFrame()
        # do a regex search
        for segment in merged:
            if segment["start"] >= last_found and re.search(
                r"\b{}\b".format(phrase), segment["text"]
            ):
                # save end timestamp of the merged segment so that we can skip over all merged segments
                # that will also satisfy the search phrase as we did a rolling merge previously
                last_found = segment["end"]
                output = pd.concat(
                    [
                        output,
                        pd.DataFrame(
                            [
                                {
                                    "start_time": segment["start"],
                                    "end_time": segment["end"],
                                }
                            ]
                        ),
                    ]
                )

        return output
