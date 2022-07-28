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
from decimal import Decimal

import numpy as np

from eva.catalog.column_type import ColumnType, NdArrayType


class ColumnTypeTests(unittest.TestCase):
    def test_ndarray_type_to_numpy_type(self):
        expected_type = [
            np.int8,
            np.uint8,
            np.int16,
            np.int32,
            np.int64,
            np.unicode_,
            np.bool_,
            np.float32,
            np.float64,
            Decimal,
            np.str_,
            np.datetime64,
        ]

        for ndarray_type, np_type in zip(NdArrayType, expected_type):
            self.assertEqual(NdArrayType.to_numpy_type(ndarray_type), np_type)

    def test_raise_exception_uknown_ndarray_type(self):
        self.assertRaises(ValueError, NdArrayType.to_numpy_type, ColumnType.TEXT)
