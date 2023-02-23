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

import pandas as pd


class AudioSearch(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.video_path = os.path.join(
            EVA_TEST_DATA_DIR, "data", "sample_videos", "touchdown.mp4"
        )

    @unittest.skip("disable test due to model downloading time")
    def test_should_return_phrase_window(self):
        from eva.udfs.audio_search import AudioSearch

        data = pd.DataFrame([{"path": self.video_path, "phrase": "rushing touchdown"}])
        audio_search = AudioSearch()
        audio_search.segment_window = 2
        audio_search.segment_overlap = 1
        result = audio_search(data)

        self.assertEqual(len(result), 1)

    @unittest.skip("disable test due to model downloading time")
    def test_should_return_phrase_windows(self):
        from eva.udfs.audio_search import AudioSearch

        data = pd.DataFrame([{"path": self.video_path, "phrase": "touchdown"}])
        audio_search = AudioSearch()
        audio_search.segment_window = 1
        audio_search.segment_overlap = 1
        result = audio_search(data)

        self.assertEqual(len(result), 2)
