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
from eva.parser.table_ref import TableInfo
from eva.parser.types import StatementType


class LoadDataStatement(AbstractStatement):
    """
    Load Data Statement constructed after parsing the input query

    Arguments:
    table (TableInfo): table to load into
    path (str): path from where data needs to be loaded
    """

    def __init__(
        self,
        table_info: TableInfo,
        path: str,
        column_list: List[AbstractExpression] = None,
        file_options: dict = None,
    ):
        super().__init__(StatementType.LOAD_DATA)
        self._table_info = table_info
        self._path = Path(path)
        self._column_list = column_list
        self._file_options = file_options

    def __str__(self) -> str:
        file_option_str = ""
        for key, value in self._file_options.items():
            file_option_str += f"{str(key)}: {str(value)}"

        column_list_str = ""
        if self._column_list is not None:
            for col in self._column_list:
                column_list_str += str(col) + ", "
            column_list_str = column_list_str.rstrip(", ")

        if self._column_list is None:
            load_stmt_str = "LOAD {} INTO {} WITH {}".format(
                self._path.name, self._table_info, file_option_str
            )
        else:
            load_stmt_str = "LOAD {} INTO {} ({}) WITH {}".format(
                self._path.name, self._table_info, column_list_str, file_option_str
            )
        return load_stmt_str

    @property
    def table_info(self) -> TableInfo:
        return self._table_info

    @property
    def path(self) -> Path:
        return self._path

    @property
    def column_list(self) -> List[AbstractExpression]:
        return self._column_list

    @column_list.setter
    def column_list(self, col_list: List[AbstractExpression]):
        self._column_list = col_list

    @property
    def file_options(self) -> dict:
        return self._file_options

    def __eq__(self, other):
        if not isinstance(other, LoadDataStatement):
            return False
        return (
            self.table_info == other.table_info
            and self.path == other.path
            and self.column_list == other.column_list
            and self.file_options == other.file_options
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.table_info,
                self.path,
                tuple(self.column_list or []),
                frozenset(self.file_options.items()),
            )
        )
