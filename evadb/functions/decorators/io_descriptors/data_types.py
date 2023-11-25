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
from typing import List, Tuple, Type, Optional

from evadb.catalog.catalog_type import ColumnType, Dimension, NdArrayType
from evadb.catalog.models.function_io_catalog import FunctionIOCatalogEntry
from evadb.functions.decorators.io_descriptors.abstract_types import (
    IOArgument,
    IOColumnArgument,
)
from evadb.utils.errors import FunctionIODefinitionError


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

# class PandasColumn:
#     def __init__(self, name: str, type: NdArrayType = NdArrayType.ANYTYPE,
#                  shape: Tuple = (None,), is_nullable: Optional[bool] = None):
#         self.name = name
#         self.type = type
#         self.shape = shape
#         self.is_nullable = is_nullable

#         assert self.name is not None, "Column name cannot be None"
#         assert self.type is not None, "Column type cannot be None"
#         assert self.shape is not None, "Column shape cannot be None. Did you mean (None,)?"

class PandasColumn(IOColumnArgument):
    def __init__(self, name: str, type: NdArrayType = NdArrayType.ANYTYPE,
                 shape: Tuple = None, is_nullable: Optional[bool] = None):

        assert name is not None, "Column name cannot be None"
        assert type is not None, "Column type cannot be None"
        assert shape is not None, "Column shape cannot be None. Did you mean (None,) to indicate any shape?"

        super().__init__(
            name=name,
            type=ColumnType.NDARRAY,
            is_nullable=is_nullable,
            array_type=type,
            array_dimensions=shape,
        )

class PandasColumnAsterick(PandasColumn):
    def __init__(self):
        super().__init__(name='*', type=NdArrayType.ANYTYPE, shape=Dimension.ANYDIM, is_nullable=None)
        
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

class NewPandasDataFrame(IOArgument):
    """Descriptor data type for Pandas Dataframe"""

    def __init__(self, columns=List[PandasColumn]) -> None:
        super().__init__()
        self.columns = columns
    
    def generate_catalog_entries(self, *args, **kwargs) -> List[type[FunctionIOCatalogEntry]]:
        assert self.columns is not None, "Columns cannot be None"
        assert len(self.columns) > 0, "Columns cannot be empty"

        catalog_entries = []
        for column in self.columns:
            catalog_entries.append(
                FunctionIOCatalogEntry(
                    name=column.name,
                    type=ColumnType.NDARRAY,
                    is_nullable=column.is_nullable,
                    array_type=column.type,
                    array_dimensions=column.shape,
                    is_input=True,
                )
            )

        return catalog_entries

class PandasDataframe(IOArgument):
    """Descriptor data type for Pandas Dataframe"""

    def __init__(self, columns, column_types=[], column_shapes=[]) -> None:
        super().__init__()
        self.columns = columns
        self.column_types = column_types
        self.column_shapes = column_shapes

    def generate_catalog_entries(
        self, is_input=False
    ) -> List[Type[FunctionIOCatalogEntry]]:
        catalog_entries = []

        if not self.column_types:
            self.column_types = [NdArrayType.ANYTYPE] * len(self.columns)

        if not self.column_shapes:
            self.column_shapes = [Dimension.ANYDIM] * len(self.columns)

        # check that columns, column_types and column_shapes are of same length
        if len(self.columns) != len(self.column_types) or len(self.columns) != len(
            self.column_shapes
        ):
            raise FunctionIODefinitionError(
                "columns, column_types and column_shapes should be of same length if specified. "
            )

        for column_name, column_type, column_shape in zip(
            self.columns, self.column_types, self.column_shapes
        ):
            catalog_entries.append(
                FunctionIOCatalogEntry(
                    name=column_name,
                    type=ColumnType.NDARRAY,
                    is_nullable=False,
                    array_type=column_type,
                    array_dimensions=column_shape,
                    is_input=is_input,
                )
            )

        return catalog_entries
