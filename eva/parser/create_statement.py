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
from typing import List

from eva.catalog.column_type import ColumnType, NdArrayType
from eva.parser.statement import AbstractStatement
from eva.parser.table_ref import TableRef
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
        col_dim: List[int],
        cci: ColConstraintInfo = ColConstraintInfo(),
    ):
        self._name = col_name
        self._type = col_type
        self._array_type = col_array_type
        self._dimension = col_dim or []
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
        return "{} {} {} {}".format(
            self._name, self._type, self.array_type, self._dimension
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
        return hash(
            (self.name, self.type, self.array_type, tuple(self.dimension), self.cci)
        )


class CreateTableStatement(AbstractStatement):
    """Create Table Statement constructed after parsing the input query

    Attributes:
        TableRef: table reference in the create table statement
        ColumnList: list of columns
    """

    def __init__(
        self,
        table_ref: TableRef,
        if_not_exists: bool,
        column_list: List[ColumnDefinition] = None,
    ):
        super().__init__(StatementType.CREATE)
        self._table_ref = table_ref
        self._if_not_exists = if_not_exists
        self._column_list = column_list

    def __str__(self) -> str:
        print_str = "CREATE TABLE {} ({}) ".format(self._table_ref, self._if_not_exists)
        return print_str

    @property
    def table_ref(self):
        return self._table_ref

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
            self.table_ref == other.table_ref
            and self.if_not_exists == other.if_not_exists
            and self.column_list == other.column_list
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.table_ref,
                self.if_not_exists,
                tuple(self.column_list),
            )
        )
