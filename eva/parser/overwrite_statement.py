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
from pathlib import Path
from typing import List

from eva.expression.abstract_expression import AbstractExpression
from eva.parser.statement import AbstractStatement
from eva.parser.table_ref import TableRef
from eva.parser.types import StatementType


class OverwriteStatement(AbstractStatement):
    """
    Overwrite Data Statement constructed after parsing the input query

    Arguments:
    table (TableRef): table to overwrite
    operation (AbstractExpression): overwrite the data with the result of operation
    """

    def __init__(
        self,
        table_ref: TableRef,
        operation: AbstractExpression
    ):
        super().__init__(StatementType.OVERWRITE)
        self._table_ref = table_ref
        self._operation = operation

    def __str__(self) -> str:

        overwrite_stmt_str = "OVERWRITE {} BY {}".format(
            self._table_ref, self._operation
        )
        return overwrite_stmt_str

    @property
    def table_ref(self) -> TableRef:
        return self._table_ref

    @property
    def operation(self) -> AbstractExpression:
        return self._operation

    def __eq__(self, other):
        if not isinstance(other, OverwriteStatement):
            return False
        return (
            self._table_ref == other._table_ref
            and self._operation == other._operation
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self._table_ref,
                self._operation,
            )
        )
