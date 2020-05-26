# coding=utf-8
# Copyright 2018-2020 EVA
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

from src.parser.statement import AbstractStatement

from src.parser.types import StatementType
from src.parser.table_ref import TableRef
from typing import List
from src.parser.types import ParserColumnDataType


class ColumnConstraintInformation:
    def __init__(self):
        self.nullable = False
        self.default_value = None
        self.primary = False
        self.unique = False


class ColumnDefinition:
    def __init__(self, col_name: str,
                 col_type: ParserColumnDataType, col_dim: List[int],
                 cci: ColumnConstraintInformation = None):
        self._name = col_name
        self._type = col_type
        self._dimension = col_dim

        # column constarint info
        if cci is not None:
            self._unique_column_constraint = cci.unique
            self._nullable = cci.nullable
            self._primary = cci.primary
            self._default_value = cci.default_value

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def dimension(self):
        return self._dimension

    def __str__(self):
        return '{} {} {}'.format(self._name, self._type, self._dimension)

    def __eq__(self, other):
        if not isinstance(other, ColumnDefinition):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.name == other.name and \
            self.type == other.type and self.dimension == other.dimension


class CreateTableStatement(AbstractStatement):
    """Create Table Statement constructed after parsing the input query

    Attributes:
        TableRef: table reference in the create table statement
        ColumnList: list of columns
    """

    def __init__(self,
                 table_ref: TableRef,
                 if_not_exists: bool,
                 column_list: List[ColumnDefinition] = None):
        super().__init__(StatementType.CREATE)
        self._table_ref = table_ref
        self._if_not_exists = if_not_exists
        self._column_list = column_list

    def __str__(self) -> str:
        print_str = "CREATE TABLE {} ({}) ".format(self._table_ref,
                                                   self._if_not_exists)
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
