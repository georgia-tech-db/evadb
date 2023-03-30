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

    def forward(self, data: pd.DataFrame) -> pd.DataFrame:
        # join all the individual audio segments
        audio_segments = np.concatenate(data.iloc[:, 0], axis=None)

        # get text segments from video using whisper
        result = self.model.transcribe(audio_segments, fp16=torch.cuda.is_available())
        print(result["text"])

        return pd.DataFrame(
            [
                {
                    "start_time": 0,
                    "end_time": 100,
                }
            ]
        )
