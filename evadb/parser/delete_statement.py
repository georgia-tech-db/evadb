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
from evadb.expression.abstract_expression import AbstractExpression
from evadb.parser.statement import AbstractStatement
from evadb.parser.table_ref import TableRef
from evadb.parser.types import StatementType


class DeleteTableStatement(AbstractStatement):
    """Delete Table Statement constructed after parsing the input query

    Attributes:
        TableRef: table reference in the delete table statement
        _where_clause : predicate of the select query, represented as a expression tree.
    """

    def __init__(
        self,
        table_ref: TableRef,
        where_clause: AbstractExpression = None,
    ):
        super().__init__(StatementType.DELETE)
        self._table_ref = table_ref
        self._where_clause = where_clause

    def __str__(self) -> str:
        delete_str = f"DELETE FROM {self._table_ref}"
        if self._where_clause is not None:
            delete_str += " WHERE " + str(self._where_clause)

        return delete_str

    @property
    def table_ref(self):
        return self._table_ref

    @property
    def where_clause(self):
        return self._where_clause

    def __eq__(self, other):
        if not isinstance(other, DeleteTableStatement):
            return False
        return (
            self._table_ref == other._table_ref
            and self.where_clause == other.where_clause
        )

    def __hash__(self) -> int:
        return hash((super().__hash__(), self._table_ref, self.where_clause))
