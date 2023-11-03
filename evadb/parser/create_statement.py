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
from typing import List, Tuple

from evadb.catalog.catalog_type import ColumnType, NdArrayType
from evadb.parser.select_statement import SelectStatement
from evadb.parser.statement import AbstractStatement
from evadb.parser.table_ref import TableInfo
from evadb.parser.types import StatementType


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

    @name.setter
    def name(self, value):
        self._name = value

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
        query: SelectStatement = None,
    ):
        super().__init__(StatementType.CREATE)
        self._table_info = table_info
        self._if_not_exists = if_not_exists
        self._column_list = column_list
        self._query = query

    def __str__(self) -> str:
        print_str = "CREATE TABLE {} ({}) \n".format(
            self._table_info, self._if_not_exists
        )

        if self._query is not None:
            print_str = "CREATE TABLE {} AS {}\n".format(self._table_info, self._query)

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

    @property
    def query(self):
        return self._query

    @column_list.setter
    def column_list(self, value):
        self._column_list = value

    def __eq__(self, other):
        if not isinstance(other, CreateTableStatement):
            return False
        return (
            self.table_info == other.table_info
            and self.if_not_exists == other.if_not_exists
            and self.column_list == other.column_list
            and self.query == other.query
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.table_info,
                self.if_not_exists,
                tuple(self.column_list or []),
                self.query,
            )
        )


class CreateDatabaseStatement(AbstractStatement):
    def __init__(
        self, database_name: str, if_not_exists: bool, engine: str, param_dict: dict
    ):
        super().__init__(StatementType.CREATE_DATABASE)
        self.database_name = database_name
        self.if_not_exists = if_not_exists
        self.engine = engine
        self.param_dict = param_dict

    def __eq__(self, other):
        if not isinstance(other, CreateDatabaseStatement):
            return False
        return (
            self.database_name == other.database_name
            and self.if_not_exists == other.if_not_exists
            and self.engine == other.engine
            and self.param_dict == other.param_dict
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.database_name,
                self.if_not_exists,
                self.engine,
                hash(frozenset(self.param_dict.items())),
            )
        )

    def __str__(self) -> str:
        return (
            f"CREATE DATABASE {self.database_name} \n"
            f"WITH ENGINE '{self.engine}' , \n"
            f"PARAMETERS = {self.param_dict};"
        )
