# coding=utf-8
# Copyright 2018-2023 EvaDB
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
from test.util import file_remove

import cv2
import numpy as np
import pandas as pd

from evadb.configuration.constants import EvaDB_ROOT_DIR
from evadb.udfs.ndarray.to_grayscale import ToGrayscale


class ToGrayscaleTests(unittest.TestCase):
    def setUp(self):
        self.to_grayscale_instance = ToGrayscale()

    def test_gray_scale_name_exists(self):
        assert hasattr(self.to_grayscale_instance, "name")

    def test_should_convert_to_grayscale(self):
        arr = cv2.imread(f"{EvaDB_ROOT_DIR}/test/udfs/data/dog.jpeg")
        df = pd.DataFrame([[arr]])
        modified_arr = self.to_grayscale_instance(df)["grayscale_frame_array"]
        cv2.imwrite(f"{EvaDB_ROOT_DIR}/test/udfs/data/tmp.jpeg", modified_arr[0])
        actual_array = cv2.imread(f"{EvaDB_ROOT_DIR}/test/udfs/data/tmp.jpeg")
        expected_arr = cv2.imread(f"{EvaDB_ROOT_DIR}/test/udfs/data/grayscale_dog.jpeg")
        self.assertEqual(np.sum(actual_array - expected_arr), 0)
        file_remove(Path(f"{EvaDB_ROOT_DIR}/test/udfs/data/tmp.jpeg"))
