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
from typing import List, Tuple, Type

import numpy as np
import torch

from eva.catalog.catalog_type import ColumnType, NdArrayType
from eva.catalog.models.udf_io_catalog import UdfIOCatalogEntry
from eva.udfs.decorators.io_descriptors.abstract_types import (
    IOArgument,
    IOColumnArgument,
)


class NumpyArray(IOColumnArgument):
    """Descriptor data type for Numpy Array"""

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

    def arg_name(self):
        return "NumpyArray"


class PyTorchTensor(IOColumnArgument):
    """Descriptor data type for PyTorch Tensor"""

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

    def arg_name(self):
        return "PyTorch Tensor"


class PandasDataframe(IOArgument):
    """Descriptor data type for Pandas Dataframe"""

    def __init__(self, columns, column_types=[], column_shapes=[]) -> None:
        super().__init__()
        self.columns = columns
        self.column_types = column_types
        self.column_shapes = column_shapes

    def generate_catalog_entries(self, is_input=False) -> List[Type[UdfIOCatalogEntry]]:
        catalog_entries = []

        for column_name, column_type, column_shape in zip(
            self.columns, self.column_types, self.column_shapes
        ):
            catalog_entries.append(
                UdfIOCatalogEntry(
                    name=column_name,
                    type=ColumnType.NDARRAY,
                    is_nullable=False,
                    array_type=column_type,
                    array_dimensions=column_shape,
                    is_input=is_input,
                )
            )

        return catalog_entries

    def arg_name(self):
        return "PandasDataframes"
