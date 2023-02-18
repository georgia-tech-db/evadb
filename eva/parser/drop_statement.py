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

from eva.parser.statement import AbstractStatement
from eva.parser.table_ref import TableInfo
from eva.parser.types import StatementType


class DropTableStatement(AbstractStatement):
    """Drop Table Statement constructed after parsing the input query"""

    def __init__(self, table_infos: List[TableInfo], if_exists: bool):
        super().__init__(StatementType.DROP)
        self._table_infos = table_infos
        self._if_exists = if_exists

    def __str__(self) -> str:
        ti_str = [str(t) for t in self._table_infos]
        if self._if_exists:
            return f"DROP TABLE IF EXISTS {ti_str}"
        else:
            return f"DROP TABLE {ti_str}"

    @property
    def table_infos(self):
        return self._table_infos

    @property
    def if_exists(self):
        return self._if_exists

    def __eq__(self, other):
        if not isinstance(other, DropTableStatement):
            return False
        return (
            self.table_infos == other.table_infos and self.if_exists == other.if_exists
        )

    def __hash__(self) -> int:
        return hash((super().__hash__(), tuple(self.table_infos), self.if_exists))
