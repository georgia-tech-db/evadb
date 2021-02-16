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
from src.expression.abstract_expression import AbstractExpression
from typing import List


class ExplodeStatement(AbstractStatement):
    """
    Explode Statement constructed after parsing the input query

    Attributes
    ----------
    _column_list : List[AbstractExpression]
        list of columns to be extracted from the select result
    _select_statement : SelectStatement
        The select statement to extract results from.
    **kwargs : to support other functionality
    """

    def __init__(self,
                 column_list: List[AbstractExpression] = None,
                 from_table=None,
                 **kwargs):
        super().__init__(StatementType.EXPLODE)
        self._from_table = from_table
        self._column_list = column_list

    @property
    def column_list(self):
        return self._column_list

    @column_list.setter
    def column_list(self, column_list: List[AbstractExpression]):
        self._column_list = column_list

    @property
    def from_table(self):
        return self._from_table

    @from_table.setter
    def from_table(self, from_table):
        self._from_table = from_table

    def __str__(self) -> str:
        print_str = "EXPLODE(({}), [{}])" \
            .format(self._from_table, self._column_list)
        return print_str

    def __eq__(self, other):
        if not isinstance(other, ExplodeStatement):
            return False
        return (self.column_list == other.column_list and
                self._from_table == other._from_table)
