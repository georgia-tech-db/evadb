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
from typing import Tuple
from eva.catalog.catalog_type import ColumnType, NdArrayType

from eva.udfs.contrib.decorators.ish.io_descriptors.eva_arguments import EvaArgument
from eva.utils.errors import TypeException


class NumpyArray(EvaArgument):
    """EVA data type for Numpy Array"""

    def __init__(self, name: str, is_nullable: bool = False, type: NdArrayType = None, dimensions: Tuple[int] = None) -> None:
        super().__init__(name=name, type=ColumnType.NDARRAY, is_nullable=is_nullable, array_type=type, array_dimensions=dimensions)

    def check_type(self, input_object) -> bool:
        if self.array_type:
            if self.array_type == "int32":
                return isinstance(input_object, np.ndarray) and (
                    input_object.dtype == np.int32
                )
            elif self.array_type == "float16":
                return isinstance(input_object, np.ndarray) and (
                    input_object.dtype == np.float16
                )
            elif self.array_type == "float32":
                return isinstance(input_object, np.ndarray) and (
                    input_object.dtype == np.float32
                )

        elif not self.array_type:
            return isinstance(input_object, np.ndarray)

    def convert_data_type(self, input_object: any):
        try:
            arr = np.asarray(input_object)
            if self.array_type == "int32":
                return arr.astype(np.int32)
            elif self.array_type == "float16":
                return arr.astype(np.float16)
            elif self.array_type == "float32":
                return arr.astype(np.float32)
            elif not self.array_type:
                return arr

        except Exception as e:
            raise TypeException(
                "Cannot convert the input object to the required type. Error message: "
                + str(e)
            )

    def check_shape(self, input_object) -> bool:
        if self.shape:
            if input_object.shape != self.shape:
                return False

        return True

    def reshape(self, input_object):
        try:
            return np.reshape(input_object, self.shape)

        except Exception as e:

            raise TypeException(
                "The input object cannot be reshaped to %s. Error is %s"
                % (self.shape, str(e))
            )

    def name(self):
        return "NumpyArray"
