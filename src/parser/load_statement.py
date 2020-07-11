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
from pathlib import Path


class LoadDataStatement(AbstractStatement):
    """
    Load Data Statement constructed after parsing the input query

    Arguments:
    table (TableRef): table reference to load into
    path (str): path from where data needs to be loaded
    """

    def __init__(self, table: TableRef, path: str):
        super().__init__(StatementType.LOAD_DATA)
        self._table = table
        self._path = Path(path)

    def __str__(self) -> str:
        print_str = "LOAD DATA INFILE {} INTO {}".format(
            self._path.name, self._table)
        return print_str

    @property
    def table(self) -> TableRef:
        return self._table

    @property
    def path(self) -> Path:
        return self._path
