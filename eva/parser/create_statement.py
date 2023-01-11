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
from typing import List, Tuple

from eva.catalog.catalog_type import ColumnType, NdArrayType
from eva.parser.statement import AbstractStatement
from eva.parser.table_ref import TableInfo
from eva.parser.types import StatementType


class ColConstraintInfo:
    def __init__(self, nullable=False, default_value=None, primary=False, unique=False):
        self.nullable = nullable
        self.default_value = default_value
        self.primary = primary
        self.unique = unique

    def __eq__(self, other):
        if not isinstance(other, ColConstraintInfo):
            return False
        return (
            self.nullable == other.nullable
            and self.default_value == other.default_value
            and self.primary == other.primary
            and self.unique == other.unique
        )

    def __hash__(self) -> int:
        return hash((self.nullable, self.default_value, self.primary, self.unique))


class ColumnDefinition:
    def __init__(
        self,
        col_name: str,
        col_type: ColumnType,
        col_array_type: NdArrayType,
        col_dim: Tuple[int],
        cci: ColConstraintInfo = ColConstraintInfo(),
    ):
        self._name = col_name
        self._type = col_type
        self._array_type = col_array_type
        self._dimension = col_dim or ()
        self._cci = cci

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def array_type(self):
        return self._array_type

    @property
    def dimension(self):
        return self._dimension

    @property
    def cci(self):
        return self._cci

    def __str__(self):
        dimension_str = ""
        if self._dimension is not None:
            dimension_str += "["
            for dim in self._dimension:
                dimension_str += str(dim) + ", "
            dimension_str = dimension_str.rstrip(", ")
            dimension_str += "]"

        if self.array_type is None:
            return "{} {}".format(self._name, self._type)
        else:
            return "{} {} {} {}".format(
                self._name, self._type, self.array_type, dimension_str
            )

    def __eq__(self, other):
        if not isinstance(other, ColumnDefinition):
            return False

        return (
            self.name == other.name
            and self.type == other.type
            and self.array_type == other.array_type
            and self.dimension == other.dimension
            and self.cci == other.cci
        )

    def __hash__(self) -> int:
        return hash((self.name, self.type, self.array_type, self.dimension, self.cci))


class CreateTableStatement(AbstractStatement):
    """Create Table Statement constructed after parsing the input query

    Attributes:
        TableRef: table reference in the create table statement
        ColumnList: list of columns
    """

    def __init__(
        self,
        table_info: TableInfo,
        if_not_exists: bool,
        column_list: List[ColumnDefinition] = None,
    ):
        super().__init__(StatementType.CREATE)
        self._table_info = table_info
        self._if_not_exists = if_not_exists
        self._column_list = column_list

    def __str__(self) -> str:
        print_str = "CREATE TABLE {} ({}) \n".format(
            self._table_info, self._if_not_exists
        )

        for column in self.column_list:
            print_str += str(column) + "\n"

        return print_str

    @property
    def table_info(self):
        return self._table_info

    @property
    def if_not_exists(self):
        return self._if_not_exists

    @property
    def column_list(self):
        return self._column_list

    def __eq__(self, other):
        if not isinstance(other, CreateTableStatement):
            return False
        return (
            self.table_info == other.table_info
            and self.if_not_exists == other.if_not_exists
            and self.column_list == other.column_list
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.table_info,
                self.if_not_exists,
                tuple(self.column_list or []),
            )
        )
