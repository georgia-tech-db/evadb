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
from test.util import file_remove

import cv2
import numpy as np
import pandas as pd

from eva.configuration.constants import EVA_ROOT_DIR
from eva.udfs.ndarray.gaussian_blur import GaussianBlur


class GaussianBlurTests(unittest.TestCase):
    def setUp(self):
        self.gb_instance = GaussianBlur()

    def tearDown(self):
        file_remove(Path(f"{EVA_ROOT_DIR}/test/udfs/data/tmp.jpeg"))

    def test_gb_name_exists(self):
        assert hasattr(self.gb_instance, "name")

    def test_should_blur_image(self):
        arr = cv2.imread(f"{EVA_ROOT_DIR}/test/udfs/data/dog.jpeg")
        df = pd.DataFrame([[arr]])
        modified_arr = self.gb_instance(df)["blurred_frame_array"]
        cv2.imwrite(
            f"{EVA_ROOT_DIR}/test/udfs/data/tmp.jpeg",
            cv2.cvtColor(modified_arr[0], cv2.COLOR_RGB2BGR),
        )

        actual_array = cv2.imread(f"{EVA_ROOT_DIR}/test/udfs/data/tmp.jpeg")
        expected_array = cv2.imread(f"{EVA_ROOT_DIR}/test/udfs/data/blurred_dog.jpeg")
        self.assertEqual(np.sum(actual_array - expected_array), 0)
