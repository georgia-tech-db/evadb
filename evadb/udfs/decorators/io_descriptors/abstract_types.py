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
from abc import ABC, abstractmethod
from typing import List, Tuple, Type

from evadb.catalog.catalog_type import ColumnType, NdArrayType
from evadb.catalog.models.udf_io_catalog import UdfIOCatalogEntry


class IOArgument(ABC):
    """
    Base class for representing inputs/outputs (IO) of a UDF using decorators. This class defines methods
    that are common for all the IO arguments.
    """

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def generate_catalog_entries(
        self, *args, **kwargs
    ) -> List[Type[UdfIOCatalogEntry]]:
        """Generates the catalog IO entries from the Argument.

        Returns:
            list: list of catalog entries for the EvaArgument.

        """
        pass


class IOColumnArgument(IOArgument):
    """
    Base class for IO arguments that are represented individually as columns in the catalog.
    """

    @abstractmethod
    def __init__(
        self,
        name: str = None,
        type: ColumnType = None,
        is_nullable: bool = None,
        array_type: NdArrayType = None,
        array_dimensions: Tuple[int] = None,
    ) -> None:
        """The parameters like shape, data type are passed as parameters to be initialized

        Args:
            shape (tuple[int]): a tuple of integers of the required shape.
            dtype (str): datatype of the elements. Types are int32, float16 and float32.

        """
        self.name = name
        self.type = type
        self.is_nullable = is_nullable
        self.array_type = array_type
        self.array_dimensions = array_dimensions

    def generate_catalog_entries(self, is_input=False) -> List[Type[UdfIOCatalogEntry]]:
        """Generates the catalog IO entries from the Argument.

        Returns:
            list: list of catalog entries for the EvaArgument.

        """
        return [
            UdfIOCatalogEntry(
                name=self.name,
                type=self.type,
                is_nullable=self.is_nullable,
                array_type=self.array_type,
                array_dimensions=self.array_dimensions,
                is_input=is_input,
            )
        ]
