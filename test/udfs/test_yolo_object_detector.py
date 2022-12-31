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
import numpy as np
import pandas as pd
import torch

NUM_FRAMES = 10


def numpy_to_yolo_format(numpy_image):
    numpy_image = numpy_image.astype(np.float64)
    numpy_image = numpy_image / 255
    r = torch.tensor(numpy_image[:, :, 0])
    g = torch.tensor(numpy_image[:, :, 1])
    b = torch.tensor(numpy_image[:, :, 2])
    rgb = torch.stack((r, g, b), dim=0)
    rgb = rgb.unsqueeze(0)
    return rgb


class YoloV5Test(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_path = os.path.dirname(os.path.abspath(__file__))

    def _load_image(self, path):
        img = cv2.imread(path)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    def test_should_raise_import_error_with_missing_torch(self):
        with self.assertRaises(ImportError):
            with mock.patch.dict(sys.modules, {"torch": None}):
                from eva.udfs.yolo_object_detector import YoloV5  # noqa: F401

                pass

    @unittest.skip("disable test due to model downloading time")
    def test_should_return_batches_equivalent_to_number_of_frames(self):
        from eva.udfs.yolo_object_detector import YoloV5

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
        test_df_dog = pd.DataFrame([frame_dog])
        test_df_cat = pd.DataFrame([frame_dog_cat])
        frame_dog = numpy_to_yolo_format(test_df_dog["data"].values[0])
        frame_cat = numpy_to_yolo_format(test_df_cat["data"].values[0])
        detector = YoloV5()
        result = []
        result.append(detector.forward(frame_dog))
        result.append(detector.forward(frame_cat))

        self.assertEqual(["dog"], result[0]["labels"].tolist()[0])
        self.assertEqual(["cat", "dog"], result[1]["labels"].tolist()[0])
