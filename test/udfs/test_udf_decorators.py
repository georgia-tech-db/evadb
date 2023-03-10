# coding=utf-8
# Copyright 2018-2022 EVA

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
import pytest
import torch

from eva.udfs.contrib.decorators.ish.io_descriptors.data_types.type_numpy import (
    NumpyArray,
)
from eva.udfs.contrib.decorators.ish.io_descriptors.data_types.type_tensor import (
    PyTorchTensor,
)
from eva.udfs.contrib.decorators.ish.udf_decorators import forward
from eva.utils.errors import TypeException


@forward(input_signature=NumpyArray(), output_signature=NumpyArray())
def forward_fn_numpy_no_constraints(self_obj, np_array):
    ans = np.asarray(np.sum(np_array))
    return ans


@forward(
    input_signature=NumpyArray(dtype="int32", shape=(2, 1)),
    output_signature=NumpyArray(dtype="int32", shape=(1, 1)),
)
def forward_fn_numpy_input_output_constraint(self_obj, np_array):
    ans = np.sum(np_array, axis=0)
    ans = ans.astype(np.int32)
    return np.expand_dims(ans, 1)


@forward(
    input_signature=NumpyArray(dtype="int32", shape=(2, 1)),
    output_signature=NumpyArray(dtype="int32", shape=(3, 1)),
)
def forward_fn_numpy_output_mismatch(self_obj, np_array):
    ans = np.sum(np_array, axis=0)
    ans = ans.astype(np.int32)
    return np.expand_dims(ans, 1)


@forward(input_signature=PyTorchTensor(), output_signature=PyTorchTensor())
def forward_fn_pytorch_no_constraints(self_obj, torch_tensor):
    ans = torch.sum(torch_tensor)
    return ans


@forward(
    input_signature=PyTorchTensor(dtype="int32", shape=(2, 1)),
    output_signature=PyTorchTensor(dtype="int32", shape=(1, 1)),
)
def forward_fn_pytorch_input_output_constraint(self_obj, torch_tensor):
    ans = torch.sum(torch_tensor)
    ans = ans.to(torch.int32)
    ans = torch.unsqueeze(ans, 0)
    ans = torch.unsqueeze(ans, 0)
    return ans


# skip this test for now
class UdfDecoratorTest(unittest.TestCase):
    @pytest.skip("skip this test for now")
    @pytest.mark.torchtest
    def test_forward_fn_numpy_no_constraints(self):
        np_arr = np.ones((10, 1))
        ans = forward_fn_numpy_no_constraints(None, np_arr)
        self.assertTrue(np.equal(ans, 10))

    @pytest.skip("skip this test for now")
    @pytest.mark.torchtest
    def test_forward_fn_numpy_with_constraints(self):
        # all the constraints are satisfied
        np_arr = np.ones((2, 1), dtype=np.int32)
        ans = forward_fn_numpy_input_output_constraint(None, np_arr)
        self.assertTrue(np.equal(ans, 2))

        # input shape is mismatched
        np_arr = np.ones((1, 2), dtype=np.int32)
        ans = forward_fn_numpy_input_output_constraint(None, np_arr)
        self.assertTrue(np.equal(ans, 2))

        # input data type is mismatched
        np_arr = np.ones((1, 2), dtype=np.float64)
        ans = forward_fn_numpy_input_output_constraint(None, np_arr)
        self.assertTrue(np.equal(ans, 2))

    @pytest.skip("skip this test for now")
    @pytest.mark.torchtest
    def test_forward_fn_numpy_output_mismatch(self):
        # the shape of output is different so raises an exception
        np_arr = np.ones((1, 2), dtype=np.float64)
        with self.assertRaises(TypeException):
            forward_fn_numpy_output_mismatch(None, np_arr)

    @pytest.skip("skip this test for now")
    @pytest.mark.torchtest
    def test_forward_fn_numpy_raise_exception(self):
        # the numpy array cannot be reshaped to the required shape. hence it throws an exception
        np_arr = np.ones((3, 1), dtype=np.int32)
        with self.assertRaises(TypeException):
            forward_fn_numpy_input_output_constraint(None, np_arr)

    @pytest.skip("skip this test for now")
    @pytest.mark.torchtest
    def test_forward_fn_pytorch_no_constraints(self):
        torch_tensor = torch.ones((2, 1))
        self.assertTrue(
            torch.eq(forward_fn_pytorch_no_constraints(None, torch_tensor), 2)
        )

    @pytest.skip("skip this test for now")
    @pytest.mark.torchtest
    def test_forward_fn_pytorch_with_constraints(self):
        # all the constraints are satisfied
        torch_tensor = torch.ones((2, 1))
        self.assertTrue(
            torch.eq(forward_fn_pytorch_input_output_constraint(None, torch_tensor), 2)
        )

        # input shape is mismatched
        torch_tensor = torch.ones((1, 2))
        self.assertTrue(
            torch.eq(forward_fn_pytorch_input_output_constraint(None, torch_tensor), 2)
        )

        # input data type is mismatched
        torch_tensor = torch.ones((1, 2), dtype=torch.float64)
        self.assertTrue(
            torch.eq(forward_fn_pytorch_input_output_constraint(None, torch_tensor), 2)
        )

    @pytest.skip("skip this test for now")
    @pytest.mark.torchtest
    def test_forward_fn_pytorch_raise_exception(self):
        # the tensor cannot be reshaped to the required shape
        torch_tensor = torch.ones((1, 3), dtype=torch.float64)
        with self.assertRaises(TypeException):
            forward_fn_pytorch_input_output_constraint(None, torch_tensor)
