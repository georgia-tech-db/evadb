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
from typing import List, Tuple, Type

from evadb.catalog.catalog_type import ColumnType, Dimension, NdArrayType
from evadb.catalog.models.udf_io_catalog import UdfIOCatalogEntry
from evadb.udfs.decorators.io_descriptors.abstract_types import (
    IOArgument,
    IOColumnArgument,
)
from evadb.utils.errors import UDFIODefinitionError


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


class PandasDataframe(IOArgument):
    """Descriptor data type for Pandas Dataframe"""

    def __init__(self, columns, column_types=[], column_shapes=[]) -> None:
        super().__init__()
        self.columns = columns
        self.column_types = column_types
        self.column_shapes = column_shapes

    def generate_catalog_entries(self, is_input=False) -> List[Type[UdfIOCatalogEntry]]:
        catalog_entries = []

        if not self.column_types:
            self.column_types = [NdArrayType.ANYTYPE] * len(self.columns)

        if not self.column_shapes:
            self.column_shapes = [Dimension.ANYDIM] * len(self.columns)

        # check that columns, column_types and column_shapes are of same length
        if len(self.columns) != len(self.column_types) or len(self.columns) != len(
            self.column_shapes
        ):
            raise UDFIODefinitionError(
                "columns, column_types and column_shapes should be of same length if specified. "
            )

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
