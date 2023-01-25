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


class DeleteTableStatement(AbstractStatement):
    """
    Delete Table Statement constructed after parsing the input query

    Attributes
    ----------
    TableRef: TableRef
        table reference in the delete table statement
    _where_clause : AbstractExpression
        predicate of the select query, represented as a expression tree.
    """

    def __init__(
        self,
        table_ref: TableRef,
        where_clause: AbstractExpression = None,
        orderby_clause: AbstractExpression = None,
        limit_count: AbstractExpression = None
    ):
        super().__init__(StatementType.DELETE)
        self._table_ref = table_ref
        self._where_clause = where_clause
        self._orderby_list = orderby_clause
        self._limit_count = limit_count

    def __str__(self) -> str:
        delete_str = "DELETE FROM {}".format(
            self._table
        )
        if self._where_clause is not None:
            delete_str += " WHERE " + str(self._where_clause)
        
        return delete_str

    @property
    def table_ref(self):
        return self._table
    
    @property
    def where_clause(self):
        return self._where_clause

    @where_clause.setter
    def where_clause(self, where_expr: AbstractExpression):
        self._where_clause = where_expr
    
    def __eq__(self, other):
        if not isinstance(other, DeleteTableStatement):
            return False
        return (
            self._table == other._table
            and self.where_clause == other.where_clause
        )
    
    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.table,
                tuple(self.where_clause)
            )
        )
    
