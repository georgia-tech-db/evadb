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
from numpy import asarray
from PIL import Image

from eva.configuration.constants import EVA_ROOT_DIR
from eva.udfs.ndarray.to_grayscale import ToGrayscale
from eva.udfs.ndarray.gaussian_blur import GaussianBlur
from eva.udfs.ndarray.horizontal_flip import HorizontalFlip
from eva.udfs.ndarray.vertical_flip import VerticalFlip
from eva.udfs.ndarray.annotate import Annotate

class OverwriteTests(unittest.TestCase):
    def setUp(self):
        self.to_grayscale_instance = ToGrayscale()
        self.gb_instance = GaussianBlur()
        self.horizontal_flip_instance = HorizontalFlip()
        self.vertical_flip_instance = VerticalFlip()
        self.annotate_instance = Annotate()

    def test_name_attr_exists(self):
        assert hasattr(self.to_grayscale_instance, "name")
        assert hasattr(self.gb_instance, "name")
        assert hasattr(self.horizontal_flip_instance, "name")
        assert hasattr(self.vertical_flip_instance, "name")
        assert hasattr(self.annotate_instance, "name")

    def test_should_flip_horizontally(self):
        img = Image.open(
            f"{EVA_ROOT_DIR}/test/data/uadetrac/small-data/MVI_20011/img00001.jpg"
        )
        arr = asarray(img)
        df = pd.DataFrame([[arr]])
        modified_arr = self.to_grayscale_instance(df)["grayscale_frame_array"]

        self.assertNotEqual(np.sum(arr - modified_arr[0]), 0)

    def test_should_blur_image(self):
        arr = asarray(Image.open(f"{EVA_ROOT_DIR}/test/udfs/data/dog.jpeg"))
        df = pd.DataFrame([[arr]])
        modified_arr = self.gb_instance(df)["blurred_frame_array"]

        data = Image.fromarray(modified_arr[0])
        data.save(f"{EVA_ROOT_DIR}/test/udfs/data/tmp.jpeg")

        actual_array = asarray(Image.open(f"{EVA_ROOT_DIR}/test/udfs/data/tmp.jpeg"))

        expected_array = asarray(Image.open(f"{EVA_ROOT_DIR}/test/udfs/data/tmp.jpeg"))

        self.assertEqual(np.sum(actual_array - expected_array), 0)

    def test_should_flip_horizontally(self):
        img = Image.open(
            f"{EVA_ROOT_DIR}/test/data/uadetrac/small-data/MVI_20011/img00001.jpg"
        )
        arr = asarray(img)
        df = pd.DataFrame([[arr]])
        flipped_arr = self.horizontal_flip_instance(df)[
            "horizontally_flipped_frame_array"
        ]

        self.assertEqual(np.sum(arr[:, 0] - np.flip(flipped_arr[0][:, -1], 1)), 0)

    def test_should_flip_vertically(self):
        img = Image.open(
            f"{EVA_ROOT_DIR}/test/data/uadetrac/small-data/MVI_20011/img00001.jpg"
        )
        arr = asarray(img)
        df = pd.DataFrame([[arr]])
        flipped_arr = self.vertical_flip_instance(df)["vertically_flipped_frame_array"]

        self.assertEqual(np.sum(arr[0, :] - np.flip(flipped_arr[0][-1, :], 1)), 0)

    def test_should_annotate(self):
        img = Image.open(
            f"{EVA_ROOT_DIR}/test/data/uadetrac/small-data/MVI_20011/img00001.jpg"
        )
        arr = asarray(img)
        arr_copy = 0 + arr
        object_type = np.array(["object"])
        bbox = np.array([[50, 50, 70, 70]])
        df = pd.DataFrame([[arr, object_type, bbox]])
        modified_arr = self.annotate_instance(df)["annotated_frame_array"]

        self.assertNotEqual(np.sum(arr_copy - modified_arr[0]), 0)
        self.assertEqual(np.sum(modified_arr[0][50][50] - np.array([207, 248, 64])), 0)
