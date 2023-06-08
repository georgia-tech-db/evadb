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

from evadb.catalog.catalog_type import NdArrayType
from evadb.udfs.decorators.decorators import forward, setup
from evadb.udfs.decorators.io_descriptors.data_types import NumpyArray, PandasDataframe


class DecoratorTests(unittest.TestCase):
    def test_setup_flags_are_updated(self):
        @setup(cacheable=True, udf_type="classification", batchable=True)
        def setup_func():
            pass

        setup_func()
        self.assertTrue(setup_func.tags["cacheable"])
        self.assertTrue(setup_func.tags["batchable"])
        self.assertEqual(setup_func.tags["udf_type"], "classification")

    def test_setup_flags_are_updated_with_default_values(self):
        @setup()
        def setup_func():
            pass

        setup_func()
        self.assertFalse(setup_func.tags["cacheable"])
        self.assertTrue(setup_func.tags["batchable"])
        self.assertEqual(setup_func.tags["udf_type"], "Abstract")

    def test_forward_flags_are_updated(self):
        input_type = PandasDataframe(
            columns=["Frame_Array"],
            column_types=[NdArrayType.UINT8],
            column_shapes=[(3, 256, 256)],
        )
        output_type = NumpyArray(
            name="label",
            type=NdArrayType.STR,
        )

        @forward(input_signatures=[input_type], output_signatures=[output_type])
        def forward_func():
            pass

        forward_func()
        self.assertEqual(forward_func.tags["input"], [input_type])
        self.assertEqual(forward_func.tags["output"], [output_type])
