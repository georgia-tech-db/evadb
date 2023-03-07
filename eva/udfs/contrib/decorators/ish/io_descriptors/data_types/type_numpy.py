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
import numpy as np

from eva.udfs.contrib.decorators.ish.io_descriptors.eva_arguments import EvaArgument
from eva.utils.errors import TypeException

class NumpyArray(EvaArgument):
    """EVA data type for Numpy Array"""
    
    def __init__(self, shape=None, dtype=None) -> None:
        super().__init__()
        self.shape = shape
        self.dtype = dtype

    def check_type(self, input_object) -> bool:
        if self.dtype:
            if self.dtype == "int32":
                return isinstance(input_object, np.ndarray) and (
                    input_object.dtype == np.int32
                )
            elif self.dtype == "float16":
                return isinstance(input_object, np.ndarray) and (
                    input_object.dtype == np.float16
                )
            elif self.dtype == "float32":
                return isinstance(input_object, np.ndarray) and (
                    input_object.dtype == np.float32
                )

        elif (not self.dtype):
            return isinstance(input_object, np.ndarray)

    def convert_data_type(self, input_object: any):
        try:
            arr = np.asarray(input_object)
            if self.dtype == "int32":
                return arr.astype(np.int32)
            elif self.dtype == "float16":
                return arr.astype(np.float16)
            elif self.dtype == "float32":
                return arr.astype(np.float32)
            elif (not self.dtype):
                return arr
            
        except:
            raise TypeException("Cannot convert the input object to the required type")
            

    def check_shape(self, input_object) -> bool:
        if self.shape:
            if input_object.shape != self.shape:
                return False

        return True

    def reshape(self, input_object):
        try:
            return np.reshape(input_object, self.shape)
        except:
            raise TypeException("The input object cannot be reshaped to %s" % (self.shape,))
        
    
    
    
    def name(self):
        return "NumpyArray"
