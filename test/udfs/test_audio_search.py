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

import os
import unittest
from test.util import EVA_TEST_DATA_DIR

import librosa
import pandas as pd

from eva.utils.generic_utils import extract_audio


class AudioSearch(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.video_path = os.path.join(
            EVA_TEST_DATA_DIR, "data", "sample_videos", "touchdown.mp4"
        )

    def _load_audio(self, path):
        audio_file = extract_audio(path)
        return librosa.load(audio_file, sr=16_000)

    def test_should_return_phrase_window(self):
        from eva.udfs.audio_search import AudioSearch

        audio_array, _ = self._load_audio(self.video_path)
        data = pd.DataFrame([{"data": audio_array, "phrase": "rushing touchdown"}])
        audio_search = AudioSearch()
        audio_search.segment_window = 2
        audio_search.segment_overlap = 1
        result = audio_search(data)

        self.assertEqual(len(result), 1)

    def test_should_return_phrase_windows(self):
        from eva.udfs.audio_search import AudioSearch

        audio_array, _ = self._load_audio(self.video_path)
        data = pd.DataFrame([{"data": audio_array, "phrase": "touchdown"}])
        audio_search = AudioSearch()
        audio_search.segment_window = 1
        audio_search.segment_overlap = 1
        result = audio_search(data)

        self.assertEqual(len(result), 2)
