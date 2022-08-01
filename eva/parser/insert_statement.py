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

from eva.expression.abstract_expression import AbstractExpression
from eva.parser.statement import AbstractStatement
from eva.parser.table_ref import TableRef
from eva.parser.types import StatementType


class InsertTableStatement(AbstractStatement):
    """
    Insert Table Statement constructed after parsing the input query

    Attributes
    ----------
    TableRef:
        table reference in the insert table statement
    ColumnList:
        list of columns
    ValueList:
        list of values to fill
    """

    def __init__(
        self,
        table: TableRef,
        column_list: List[AbstractExpression] = None,
        value_list: List[AbstractExpression] = None,
    ):
        super().__init__(StatementType.INSERT)
        self._table = table
        self._column_list = column_list
        self._value_list = value_list

    def __str__(self) -> str:
        print_str = "INSERT INTO {}({}) VALUES ({}) ".format(
            self._table, self._column_list, self._value_list
        )
        return print_str

    @property
    def table(self) -> TableRef:
        return self._table

    @property
    def column_list(self) -> List[AbstractExpression]:
        return self._column_list

    @property
    def value_list(self) -> List[AbstractExpression]:
        return self._value_list

    def __eq__(self, other):
        if not isinstance(other, InsertTableStatement):
            return False
        return (
            self.table == other.table
            and self.column_list == other.column_list
            and self.value_list == other.value_list
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.table,
                tuple(self.column_list),
                tuple(self.value_list),
            )
        )
