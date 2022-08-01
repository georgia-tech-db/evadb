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
import sys
import unittest

import cv2
import mock
import pandas as pd

from eva.models.storage.batch import Batch

NUM_FRAMES = 10


class FastRCNNObjectDetectorTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_path = os.path.dirname(os.path.abspath(__file__))

    def _load_image(self, path):
        img = cv2.imread(path)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    def test_should_raise_import_error_with_missing_torch(self):
        with self.assertRaises(ImportError):
            with mock.patch.dict(sys.modules, {"torch": None}):
                from eva.udfs.fastrcnn_object_detector import (  # noqa: F401
                    FastRCNNObjectDetector,
                )

                pass

    def test_should_raise_import_error_with_missing_torchvision(self):
        with self.assertRaises(ImportError):
            with mock.patch.dict(sys.modules, {"torchvision": None}):
                from eva.udfs.fastrcnn_object_detector import (  # noqa: F401
                    FastRCNNObjectDetector,
                )

                pass

    @unittest.skip("disable test due to model downloading time")
    def test_should_return_batches_equivalent_to_number_of_frames(self):
        from eva.udfs.fastrcnn_object_detector import FastRCNNObjectDetector

        frame_dog = {
            "id": 1,
            "data": self._load_image(os.path.join(self.base_path, "data", "dog.jpeg")),
        }
        frame_dog_cat = {
            "id": 2,
            "data": self._load_image(
                os.path.join(self.base_path, "data", "dog_cat.jpg")
            ),
        }
        frame_batch = Batch(pd.DataFrame([frame_dog, frame_dog_cat]))
        detector = FastRCNNObjectDetector()
        result = detector.classify(frame_batch)

        self.assertEqual(["dog"], result[0].labels)
        self.assertEqual(["cat", "dog"], result[1].labels)
