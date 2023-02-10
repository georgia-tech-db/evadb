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

import string

import faiss
import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer

from eva.udfs.abstract.abstract_udf import AbstractUDF
from eva.utils.generic_utils import extract_audio

try:
    import whisper
except ImportError as e:
    raise ImportError(
        f"Failed to import with error {e}, \
        please try `pip install openai-whisper`"
    )


class SemanticSearch(AbstractUDF):

    @property
    def name(self) -> str:
        return "SemanticSearch"

    def setup(self):
        self.transcriber = whisper.load_model("base")
        self.transformer = SentenceTransformer('sentence-transformers/nli-mpnet-base-v2')
        self.segment_window = 3
        self.segment_overlap = 2

    def forward(self, data: pd.DataFrame) -> pd.DataFrame:
        video_path = data.iloc[0].values[0]
        # string translator for removing punctuation
        punctuation_translator = str.maketrans('', '', string.punctuation)
        phrase = data.iloc[0].values[1].translate(punctuation_translator).lower().strip()

        # get text segments from video using whisper
        segments = []
        with extract_audio(video_path) as audio_path:
            result = self.transcriber.transcribe(audio_path, fp16=False)
            for segment in result['segments']:
                segments.append({
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'].translate(punctuation_translator).lower().strip()
                })

        # do a rolling merge of the text segments, as the search phrase may extend over multiple segments
        merged = []
        for first in range(0, len(segments), self.segment_overlap):
            last = min(len(segments) - 1, first + self.segment_window)
            text = ' '.join(segment['text'] for segment in segments[first:last])
            merged.append({
                'start': segments[first]['start'],
                'end': segments[last]['end'],
                'text': text
            })

        del segments

        df = pd.DataFrame(merged)

        # TODO: cache index
        index = self.build_index(df)

        _, doc_ids = self.search_index(index, phrase)

        output = df.loc[doc_ids[0], ['start', 'end']]
        output.rename(columns={'start': 'start_time', 'end': 'end_time'}, inplace=True)

        intervals = []
        row_ids = []
        idx = 0
        for row in output.values.tolist():
            if not self.has_overlap(row[0], row[1], intervals):
                intervals.append([row[0], row[1]])
                row_ids.append(idx)
            idx = idx + 1

        return output.loc[row_ids]

    def build_index(self, df: pd.DataFrame):
        embeddings = self.transformer.encode(df['text'].tolist())

        embeddings = np.array([embedding for embedding in embeddings]).astype("float32")

        index = faiss.IndexFlatL2(embeddings.shape[1])
        index = faiss.IndexIDMap(index)

        ids = np.array(range(0, len(df)))
        ids = np.asarray(ids.astype('int64'))
        index.add_with_ids(embeddings, ids)

        return index

    def search_index(self, index, query: str, limit=3):
        vector = self.transformer.encode([query])
        return index.search(np.array(vector).astype("float32"), k=limit)

    def has_overlap(self, start, end, intervals):
        for interval in intervals:
            if max(start, interval[0]) < min(end, interval[1]):
                return True
        return False
