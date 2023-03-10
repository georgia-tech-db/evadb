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
from typing import Tuple

import numpy as np
import pandas as pd
import torch
from eva.catalog.catalog_type import ColumnType, NdArrayType

from eva.io_descriptors.eva_arguments import EvaArgument


class NumpyArray(EvaArgument):
    """EVA data type for Numpy Array"""

    def __init__(
        self,
        name: str,
        is_nullable: bool = False,
        type: NdArrayType = None,
        dimensions: Tuple[int] = None,
    ) -> None:
        super().__init__(
            name=name,
            type=ColumnType.NDARRAY,
            is_nullable=is_nullable,
            array_type=type,
            array_dimensions=dimensions,
        )

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

        elif not self.dtype:
            return isinstance(input_object, np.ndarray)

    def check_shape(self, input_object) -> bool:
        if self.shape:
            if input_object.shape != self.shape:
                return False

        return True

    def name(self):
        return "NumpyArray"


class PyTorchTensor(EvaArgument):
    """EVA data type for PyTorch Tensor"""

    def __init__(
        self,
        name: str,
        is_nullable: bool = False,
        type: NdArrayType = None,
        dimensions: Tuple[int] = None,
    ) -> None:
        super().__init__(
            name=name,
            type=ColumnType.NDARRAY,
            is_nullable=is_nullable,
            array_type=type,
            array_dimensions=dimensions,
        )

    def check_type(self, input_object) -> bool:
        if self.array_type:
            if self.array_type == "int32":
                return isinstance(input_object, torch.Tensor) and (
                    input_object.dtype == torch.int32
                )
            elif self.array_type == "float16":
                return isinstance(input_object, torch.Tensor) and (
                    input_object.dtype == torch.float16
                )
            elif self.array_type == "float32":
                return isinstance(input_object, torch.Tensor) and (
                    input_object.dtype == torch.float32
                )

        elif not self.array_type:
            return isinstance(input_object, torch.Tensor)

    def check_shape(self, input_object) -> bool:
        if self.shape:
            if input_object.shape != self.shape:
                return False

        return True

    def name(self):
        return "PyTorch Tensor"


class PandasDataframe(EvaArgument):
    """EVA data type for Pandas Dataframe"""

    def __init__(self, columns) -> None:
        super().__init__()
        self.columns = columns

    def check_shape(self, input_object: any, required_shape: tuple = None) -> bool:
        return True

    def check_column_names(self, input_object):
        obj_cols = list(input_object.columns)
        return obj_cols == self.columns

    def check_type(self, input_object) -> bool:
        return isinstance(input_object, pd.DataFrame)

    def is_output_columns_set(self):
        return not (self.columns is None)

    def name(self):
        return "PandasDataframe"
