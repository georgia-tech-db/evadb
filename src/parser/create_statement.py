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
from src.parser.table_ref import TableRef
from typing import List
from src.catalog.models.df_column import DataFrameColumn


class CreateTableStatement(AbstractStatement):
    """Create Table Statement constructed after parsing the input query

    Attributes:
        TableRef: table reference in the create table statement
        ColumnList: list of columns
    """

    def __init__(self,
                 table_name: TableRef,
                 if_not_exists: bool,
                 column_list: List[DataFrameColumn] = None):
        super().__init__(StatementType.CREATE)
        self._table_name = table_name
        self._if_not_exists = if_not_exists
        self._column_list = column_list

    def __str__(self) -> str:
        print_str = "CREATE TABLE {} ({}) ".format(self._table_name,
                                                   self._if_not_exists)
        return print_str
