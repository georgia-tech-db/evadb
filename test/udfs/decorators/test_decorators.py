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
import torch

from eva.catalog.catalog_type import NdArrayType
from eva.udfs.decorators.decorators import forward, setup
from eva.udfs.decorators.io_descriptors.data_types import (
    NumpyArray,
    PandasDataframe,
    PyTorchTensor,
)
from eva.utils.errors import UDFIODefinitionError


class DecoratorTests(unittest.TestCase):
    def test_setup_flags_are_updated(self):
        @setup(cachable=True, udf_type="classification", batchable=True)
        def setup_func():
            pass

        setup_func()
        self.assertTrue(setup_func.tags["cachable"])
        self.assertTrue(setup_func.tags["batchable"])
        self.assertEqual(setup_func.tags["udf_type"], "classification")

    def test_setup_flags_are_updated_with_default_values(self):
        @setup()
        def setup_func():
            pass

        setup_func()
        self.assertFalse(setup_func.tags["cachable"])
        self.assertTrue(setup_func.tags["batchable"])
        self.assertEqual(setup_func.tags["udf_type"], "Abstract")

    def test_forward_flags_are_updated(self):
        input_type = PandasDataframe(
            columns=["Frame_Array"],
            column_types=[NdArrayType.UINT8],
            column_shapes=[(3, 256, 256)],
        )
        output_type = NumpyArray(name="label", type=NdArrayType.STR,)

        @forward(input_signatures=[input_type], output_signatures=[output_type])
        def forward_func():
            pass

        forward_func()
        self.assertEqual(forward_func.tags["input"], [input_type])
        self.assertEqual(forward_func.tags["output"], [output_type])

    # check the different constraints on shapes: same shape, can be reshaped, cannot be reshaped

    # numpy array
    # input shapes are same
    def test_forward_numpy_input_shapes_are_matched(self):
        @forward(
            input_signatures=[
                NumpyArray(
                    name="input_arr",
                    is_nullable=False,
                    type=NdArrayType.INT32,
                    dimensions=(2, 2),
                )
            ],
            output_signatures=[
                NumpyArray(
                    name="output",
                    is_nullable=False,
                    type=NdArrayType.INT32,
                    dimensions=(2, 1),
                )
            ],
        )
        def forward_func_shape_matched(self, input_obj):
            ans = np.sum(input_obj, axis=1)
            ans = np.expand_dims(ans, 1)
            return ans

        input_object_1 = np.ones((2, 2))
        func_output = forward_func_shape_matched(None, input_object_1)
        self.assertTrue(np.all(np.equal(func_output, np.asarray([[2], [2]]))))

    def test_forward_func_numpy_input_reshaped(self):
        # input can be reshaped and data types can be converted
        @forward(
            input_signatures=[
                NumpyArray(
                    name="input_arr",
                    is_nullable=False,
                    type=NdArrayType.INT32,
                    dimensions=(3, 2),
                )
            ],
            output_signatures=[
                NumpyArray(
                    name="output",
                    is_nullable=False,
                    type=NdArrayType.INT32,
                    dimensions=(3, 1),
                )
            ],
        )
        def forward_func_input_mismatch(self, input_obj):
            ans = np.sum(input_obj, axis=1)
            ans = np.expand_dims(ans, 1)
            return ans

        input_object_1 = np.ones((2, 3), dtype=np.float32)
        func_output = forward_func_input_mismatch(None, input_object_1)

        self.assertTrue(np.all(np.equal(func_output, np.asarray([[2], [2], [2]]))))

    def test_forward_func_numpy_input_shape_mismatched(self):
        # input cannot be reshaped
        @forward(
            input_signatures=[
                NumpyArray(
                    name="input_arr",
                    is_nullable=False,
                    type=NdArrayType.INT32,
                    dimensions=(3, 2),
                )
            ],
            output_signatures=[
                NumpyArray(
                    name="output",
                    is_nullable=False,
                    type=NdArrayType.INT32,
                    dimensions=(3, 1),
                )
            ],
        )
        def forward_func_input_mismatch(self, input_obj):
            ans = np.sum(input_obj, axis=1)
            ans = np.expand_dims(ans, 1)
            return ans

        input_object_1 = np.ones((4, 3))
        with self.assertRaises(UDFIODefinitionError):
            forward_func_input_mismatch(None, input_object_1)

    def test_forward_pytorch_input_shapes_are_matched(self):
        @forward(
            input_signatures=[
                PyTorchTensor(
                    name="input_arr",
                    is_nullable=False,
                    type=NdArrayType.INT32,
                    dimensions=(2, 2),
                )
            ],
            output_signatures=[
                PyTorchTensor(
                    name="output",
                    is_nullable=False,
                    type=NdArrayType.INT32,
                    dimensions=(2, 1),
                )
            ],
        )
        def forward_func_shape_matched(self, input_obj):
            ans = torch.sum(input_obj, axis=1)
            ans = torch.unsqueeze(ans, 1)
            return ans

        input_object_1 = np.ones((2, 2))
        func_output = forward_func_shape_matched(None, input_object_1)
        self.assertTrue(torch.all(torch.eq(func_output, torch.Tensor([[2], [2]]))))

    def test_forward_pytorch_input_shapes_are_reshaped(self):
        @forward(
            input_signatures=[
                PyTorchTensor(
                    name="input_arr",
                    is_nullable=False,
                    type=NdArrayType.INT32,
                    dimensions=(3, 2),
                )
            ],
            output_signatures=[
                PyTorchTensor(
                    name="output",
                    is_nullable=False,
                    type=NdArrayType.INT32,
                    dimensions=(3, 1),
                )
            ],
        )
        def forward_func_shape_matched(self, input_obj):
            ans = torch.sum(input_obj, axis=1)
            ans = torch.unsqueeze(ans, 1)
            return ans

        input_object_1 = np.ones((2, 3), dtype=torch.float32)
        func_output = forward_func_shape_matched(None, input_object_1)
        self.assertTrue(torch.all(torch.eq(func_output, torch.Tensor([[2], [2], [2]]))))

    def test_forward_pytorch_input_shapes_are_mismatched(self):
        @forward(
            input_signatures=[
                PyTorchTensor(
                    name="input_arr",
                    is_nullable=False,
                    type=NdArrayType.INT32,
                    dimensions=(3, 2),
                )
            ],
            output_signatures=[
                PyTorchTensor(
                    name="output",
                    is_nullable=False,
                    type=NdArrayType.INT32,
                    dimensions=(3, 1),
                )
            ],
        )
        def forward_func_shape_matched(self, input_obj):
            ans = torch.sum(input_obj, axis=1)
            ans = torch.unsqueeze(ans, 1)
            return ans

        input_object_1 = np.ones((4, 3))

        with self.assertRaises(UDFIODefinitionError):
            forward_func_shape_matched(None, input_object_1)

    def test_forward_pandas_output_matched(self):
        @forward(
            input_signatures=[],
            output_signatures=[
                PandasDataframe(
                    columns=["A", "B"],
                    column_types=[NdArrayType.STR, NdArrayType.STR],
                    column_shapes=[(None,), (None,)],
                )
            ],
        )
        def forward_func_output_matched(self, input_obj):
            df = pd.DataFrame({"A": ["a", "a"], "B": ["b", "b"]})
            return df

        output = forward_func_output_matched(None, [])
        self.assertTrue(len(output.columns) == 2)

    def test_forward_pandas_output_mismatched(self):
        @forward(
            input_signatures=[],
            output_signatures=[
                PandasDataframe(
                    columns=["A", "B"],
                    column_types=[NdArrayType.STR, NdArrayType.STR],
                    column_shapes=[(None,), (None,)],
                )
            ],
        )
        def forward_func_output_matched(self, input_obj):
            df = pd.DataFrame({"A": ["a", "a"], "B": ["b", "b"], "C": ["c", "c"]})
            return df

        with self.assertRaises(UDFIODefinitionError):
            forward_func_output_matched(None, [])


if __name__ == "__main__":
    suite = unittest.TestSuite()
    my_tests = DecoratorTests()
    suite.addTest(DecoratorTests("test_forward_pandas_output_mismatched"))
    suite.addTest(DecoratorTests("test_forward_pandas_output_matched"))
    suite.addTest(DecoratorTests("test_forward_pytorch_input_shapes_are_mismatched"))
    suite.addTest(DecoratorTests("test_forward_pytorch_input_shapes_are_reshaped"))
    suite.addTest(DecoratorTests("test_forward_pytorch_input_shapes_are_matched"))
    suite.addTest(DecoratorTests("test_forward_func_numpy_input_shape_mismatched"))
    suite.addTest(DecoratorTests("test_forward_func_numpy_input_reshaped"))
    suite.addTest(DecoratorTests("test_forward_numpy_input_shapes_are_matched"))
    unittest.TextTestRunner().run(suite)
