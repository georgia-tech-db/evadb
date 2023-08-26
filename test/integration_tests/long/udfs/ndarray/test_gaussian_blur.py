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

import numpy as np
import pandas as pd

from evadb.configuration.constants import EvaDB_ROOT_DIR
from evadb.udfs.ndarray.gaussian_blur import GaussianBlur
from evadb.utils.generic_utils import try_to_import_cv2


class GaussianBlurTests(unittest.TestCase):
    def setUp(self):
        self.gb_instance = GaussianBlur()
        self.tmp_file = f"{EvaDB_ROOT_DIR}/test/unit_tests/udfs/data/tmp.jpeg"

    def test_gb_name_exists(self):
        assert hasattr(self.gb_instance, "name")

    def test_should_blur_image(self):
        try_to_import_cv2()
        import cv2

        arr = cv2.imread(f"{EvaDB_ROOT_DIR}/test/unit_tests/udfs/data/dog.jpeg")
        df = pd.DataFrame([[arr]])
        modified_arr = self.gb_instance(df)["blurred_frame_array"]
        cv2.imwrite(
            self.tmp_file,
            cv2.cvtColor(modified_arr[0], cv2.COLOR_RGB2BGR),
        )

        actual_array = cv2.imread(self.tmp_file)
        expected_array = cv2.imread(
            f"{EvaDB_ROOT_DIR}/test/unit_tests/udfs/data/blurred_dog.jpeg"
        )
        self.assertEqual(np.sum(actual_array - expected_array), 0)
        file_remove(Path(self.tmp_file))
