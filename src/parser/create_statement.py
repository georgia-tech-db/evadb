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

from src.parser.eva_statement import EvaStatement

from src.parser.types import StatementType
from src.expression.abstract_expression import AbstractExpression
from src.parser.table_ref import TableRef
from typing import List


class CreateTableStatement(EvaStatement):
    """
    Create Table Statement constructed after parsing the input query

    Attributes
    ----------
    TableRef:
        table reference in the create table statement
    ColumnList:
        list of columns
    **kwargs : to support other functionality, Orderby, Distinct, Groupby.
    """

    def __init__(self,
                 table_name: TableRef = None,
                 column_list: List[AbstractExpression] = None):
        super().__init__(StatementType.SELECT)
        self._table_name = table_name

    def __str__(self) -> str:
        print_str = "CREATE TABLE {} ".format(self._table_name)
        return print_str
