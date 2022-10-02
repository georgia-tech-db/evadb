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

import numpy as np
import pandas as pd

from eva.udfs.ndarray.crop import Crop


class CropTests(unittest.TestCase):
    def setUp(self):
        self.crop_instance = Crop()

    def test_crop_name_exists(self):
        assert hasattr(self.crop_instance, "name")

    def test_should_crop_one_frame(self):
        imarray = np.random.randint(0, 255, size=(100, 100, 3))
        bbox = np.array([0, 0, 30, 60])
        df = pd.DataFrame([[imarray, bbox]])
        cropped_image = self.crop_instance(df)

        expected_image = pd.DataFrame(
            [[imarray[0:60, 0:30]]], columns=["cropped_frame_array"]
        )
        self.assertTrue(expected_image.equals(cropped_image))

    def test_should_crop_multi_frame(self):
        imarray = np.random.randint(0, 255, size=(100, 100, 3))
        bbox1 = np.array([0, 0, 30, 60])
        bbox2 = np.array([50, 50, 70, 70])
        bbox3 = np.array([30, 0, 60, 20])
        df = pd.DataFrame([[imarray, bbox1], [imarray, bbox2], [imarray, bbox3]])
        cropped_image = self.crop_instance(df)

        expected_image = pd.DataFrame(
            [[imarray[0:60, 0:30]], [imarray[50:70, 50:70]], [imarray[0:20, 30:60]]],
            columns=["cropped_frame_array"],
        )
        self.assertTrue(expected_image.equals(cropped_image))

    def test_should_crop_bad_bbox(self):
        imarray = np.random.randint(0, 255, size=(100, 100, 3))
        bbox1 = np.array([0, 0, 0, 0])
        bbox2 = np.array([-10, -10, 20, 20])
        df = pd.DataFrame([[imarray, bbox1], [imarray, bbox2]])
        cropped_image = self.crop_instance(df)

        expected_image = pd.DataFrame(
            [[imarray[0:1, 0:1]], [imarray[0:20, 0:20]]],
            columns=["cropped_frame_array"],
        )
        self.assertTrue(expected_image.equals(cropped_image))
