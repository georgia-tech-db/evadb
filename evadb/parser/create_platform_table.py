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

from evadb.parser.create_statement import ColumnDefinition, CreateTableStatement
from evadb.parser.select_statement import SelectStatement
from evadb.parser.statement import AbstractStatement
from evadb.parser.table_ref import TableInfo
from evadb.parser.types import StatementType


class CreatePlatformTableStatment(AbstractStatement):
    """Create Table Statement constructed after parsing the input query

    Attributes:
        TableRef: table reference in the create table statement
        ColumnList: list of columns
    """

    def __init__(
        self,
        table_info: TableInfo,
        if_not_exists: bool,
        table_platform: str,
        table_token: str,
        column_list: List[ColumnDefinition] = None,
        query: SelectStatement = None,
    ):
        super().__init__(StatementType.CREATE)
        self._table_info = table_info
        self._if_not_exists = if_not_exists
        self._table_platform = table_platform
        self._table_token = table_token
        self._column_list = column_list
        self._query = query

    def __str__(self) -> str:
        print_str = "CREATE TABLE {} PLATFORM {} ({}) \n".format(
            self._table_info, self.table_platform, self._if_not_exists
        )

        if self.table_token is not None:
            print_str = "CREATE TABLE {} PLATFORM {} TOKEN {} ({}) \n".format(
                    self._table_info, self.table_platform, self.table_token,self._if_not_exists
                )

        if self._query is not None:
            print_str = "CREATE TABLE {} PLATFORM {} AS {}\n".format(
                self._table_info,self.table_platform, self.table_token, self._query
                )
            if self.table_token is not None:
                print_str = "CREATE TABLE {} PLATFORM {} TOKEN {} AS {}\n".format(
                    self._table_info,self.table_platform, self.table_token, self._query
                    )

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
    def table_platform(self):
        return self.table_platform
    
    @property
    def table_token(self):
        return self.table_token

    @property
    def column_list(self):
        return self._column_list

    @property
    def query(self):
        return self._query

    @table_platform.setter
    def table_platform(self, value):
        self._table_platform = value

    @table_token.setter
    def table_token(self, value):
        self._table_token = value

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
                self.table_platform,
                self.table_token,
                tuple(self.column_list or []),
                self.query,
            )
        )
