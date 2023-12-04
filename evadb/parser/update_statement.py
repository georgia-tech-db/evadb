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
from typing import List

from evadb.expression.abstract_expression import AbstractExpression
from evadb.parser.statement import AbstractStatement
from evadb.parser.table_ref import TableRef
from evadb.parser.types import StatementType


class UpdateTableStatement(AbstractStatement):
    """
    Update Table Statement constructed after parsing the input query

    Attributes
    ----------
    table_ref:
        table reference in the update table statement
    column_list:
        list of columns
    value_list:
        list of values to fill
    where_clause: 
        predicate of the select query, represented as a expression tree.
    """

    def __init__(
        self,
        table_ref: TableRef,
        column_list: List[AbstractExpression] = None,
        value_list: List[AbstractExpression] = None,
        where_clause: AbstractExpression = None,
    ):
        super().__init__(StatementType.UPDATE)
        self._table_ref = table_ref
        self._column_list = column_list
        self._value_list = value_list
        self._where_clause = where_clause

    def __str__(self) -> str:
        set_str = ""
        assert len(self._column_list) == len(self._value_list)
        if self._column_list is not None and self._value_list is not None:
            for i in range(len(self._column_list)):
                column = self._column_list[i]
                value = self._value_list[i]
                set_str += str(column) + " = '" + str(value) + "', "
            set_str = set_str.rstrip(", ")

        print_str = "UPDATE {}SET {}".format(
            self._table_ref, set_str
        )
        
        if self._where_clause is not None:
            print_str += " WHERE " + str(self._where_clause)
        return print_str

    @property
    def table_ref(self) -> TableRef:
        return self._table_ref

    @property
    def column_list(self) -> List[AbstractExpression]:
        return self._column_list

    @property
    def value_list(self) -> List[AbstractExpression]:
        return self._value_list
      
    @property
    def where_clause(self):
        return self._where_clause

    def __eq__(self, other):
        if not isinstance(other, UpdateTableStatement):
            return False
        return (
            self.table_ref == other.table_ref
            and self.column_list == other.column_list
            and self.value_list == other.value_list
            and self.where_clause == other.where_clause
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.table_ref,
                tuple(self.column_list),
                tuple(self.value_list),
                self.where_clause(),
            )
        )
