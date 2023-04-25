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
import unittest
from pathlib import Path
from test.markers import windows_skip_marker
from test.util import EVA_TEST_DATA_DIR

import cv2
import pandas as pd

from eva.models.storage.batch import Batch


class HuggingFaceEmotionTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_path = Path(EVA_TEST_DATA_DIR) / "data" / "huggingface"

    def _load_image(self, path):
        assert path.exists(), f"File does not exist at the path {str(path)}"
        img = cv2.imread(str(path))
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    @windows_skip_marker
    def test_should_return_correct_number_of_faces(self):
        from eva.udfs.huggingface_emotion_detector import HuggingFaceEmotionDetector

        happy_faces = self.base_path / "happy.jpg"
        sad_faces = self.base_path / "sad.jpeg"
        frame_happy_faces = {
            "id": 1,
            "data": self._load_image(happy_faces),
        }
        frame_sad_faces = {
            "id": 2,
            "data": self._load_image(sad_faces),
        }
        frame_batch = Batch(pd.DataFrame([frame_happy_faces, frame_happy_faces]))
        detector = HuggingFaceEmotionDetector()
        result = detector(frame_batch.project(["data"]).frames)
        self.assertEqual(8, len(result.iloc[0]["bboxes"]))
        self.assertEqual(8, len(result.iloc[1]["bboxes"]))
        self.assertEqual("happy", len(result.iloc[1]["labels"][0]))

        frame_batch = Batch(pd.DataFrame([frame_sad_faces]))
        detector = HuggingFaceEmotionDetector()
        result = detector(frame_batch.project(["data"]).frames)
        self.assertEqual(5, len(result.iloc[0]["bboxes"]))
        self.assertEqual("neutral", len(result.iloc[0]["labels"][0]))
