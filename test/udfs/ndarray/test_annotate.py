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

import numpy as np
import pandas as pd
from numpy import asarray

from evadb.configuration.constants import EvaDB_ROOT_DIR
from evadb.udfs.ndarray.annotate import Annotate
from evadb.utils.generic_utils import try_to_import_pillow


class AnnotateTests(unittest.TestCase):
    def setUp(self):
        try_to_import_pillow()
        self.annotate_instance = Annotate()

    def test_annotate_name_exists(self):
        assert hasattr(self.annotate_instance, "name")

    def test_should_annotate(self):
        from PIL import Image

        img = Image.open(
            f"{EvaDB_ROOT_DIR}/test/data/uadetrac/small-data/MVI_20011/img00001.jpg"
        )
        arr = asarray(img)
        arr_copy = 0 + arr
        object_type = np.array(["object"])
        bbox = np.array([[50, 50, 70, 70]])
        df = pd.DataFrame([[arr, object_type, bbox]])
        modified_arr = self.annotate_instance(df)["annotated_frame_array"]

        self.assertNotEqual(np.sum(arr_copy - modified_arr[0]), 0)
        self.assertEqual(np.sum(modified_arr[0][50][50] - np.array([207, 248, 64])), 0)
        self.assertEqual(np.sum(modified_arr[0][70][70] - np.array([207, 248, 64])), 0)
        self.assertEqual(np.sum(modified_arr[0][50][70] - np.array([207, 248, 64])), 0)
        self.assertEqual(np.sum(modified_arr[0][70][50] - np.array([207, 248, 64])), 0)
