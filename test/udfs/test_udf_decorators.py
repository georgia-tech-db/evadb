import os
import sys
import unittest
import numpy as np
import pytest

from eva.udfs.contrib.decorators.ish.io_descriptors.data_types.type_numpy import NumpyArray
from eva.udfs.contrib.decorators.ish.io_descriptors.data_types.type_pandas_dataframe import PandasDataframe
from eva.udfs.contrib.decorators.ish.io_descriptors.data_types.type_tensor import PyTorchTensor
from eva.udfs.contrib.decorators.ish.io_descriptors.eva_arguments import EvaArgument
from eva.utils.errors import TypeException
from eva.udfs.contrib.decorators.ish.udf_decorators import setup, forward

@forward(
    input_signature=NumpyArray(), 
    output_signature=NumpyArray()
)
def forward_fn_no_constraints(self_obj, np_array):
    ans = np.asarray(np.sum(np_array))
    return ans

@forward(
    input_signature=NumpyArray(dtype="int32", shape=(2,1)), 
    output_signature=NumpyArray(dtype="int32", shape=(1,1))
)
def forward_fn_input_output_constraint(self_obj, np_array):
    ans = np.sum(np_array, axis=0)
    ans = ans.astype(np.int32)
    return np.expand_dims(ans, 1)
 

class UdfDecoratorTest(unittest.TestCase):
    @pytest.mark.torchtest
    def test_forward_fn_no_constraints(self):
        np_arr = np.ones((10, 1))
        ans = forward_fn_no_constraints(None, np_arr)
        self.assertTrue(np.equal(ans, 10))
        
    @pytest.mark.torchtest
    def test_forward_fn_with_constraints(self):
        np_arr = np.ones((2,1), dtype=np.int32)
        ans = forward_fn_input_output_constraint(None, np_arr)
        self.assertTrue(np.equal(ans, 2))

        
if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(UdfDecoratorTest("test_forward_fn_with_constraints_input_mismatch"))
    unittest.TextTestRunner().run(suite)

        
    
    
    
    
    