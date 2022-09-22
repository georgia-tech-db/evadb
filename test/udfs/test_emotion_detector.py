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
from test.util import EVA_TEST_DATA_DIR

import cv2
import pandas as pd

from eva.models.storage.batch import Batch


class EmotionDetector(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_path = Path(EVA_TEST_DATA_DIR) / "data" / "emotion_detector"

    def _load_image(self, path):
        assert path.exists(), f"File does not exist at the path {str(path)}"
        img = cv2.imread(str(path))
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    @unittest.skip("disable test due to model downloading time")
    def test_should_return_correct_emotion(self):
        from eva.udfs.emotion_detector import EmotionDetector

        happy_img = self.base_path / "happy.jpg"
        sad_img = self.base_path / "sad.jpg"
        angry_img = self.base_path / "angry.jpg"

        frame_happy = {
            "id": 1,
            "data": self._load_image(happy_img),
        }

        frame_sad = {
            "id": 2,
            "data": self._load_image(sad_img),
        }

        frame_angry = {
            "id": 3,
            "data": self._load_image(angry_img),
        }

        frame_batch = Batch(pd.DataFrame([frame_happy, frame_sad, frame_angry]))
        detector = EmotionDetector()
        result = detector.classify(frame_batch.project(["data"]).frames)

        self.assertEqual("happy", result.iloc[0]["labels"])
        self.assertEqual("sad", result.iloc[1]["labels"])
        self.assertEqual("angry", result.iloc[2]["labels"])
