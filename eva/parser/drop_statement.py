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
from eva.parser.table_ref import TableRef
from eva.parser.types import StatementType


class DropTableStatement(AbstractStatement):
    """Drop Table Statement constructed after parsing the input query

    Attributes:
        TableRef: table reference in the drop table statement
    """

    def __init__(self, table_refs: List[TableRef], if_exists: bool):
        super().__init__(StatementType.DROP)
        self._table_refs = table_refs
        self._if_exists = if_exists

    def __str__(self) -> str:
        if self._if_exists:
            print_str = "DROP TABLE IF EXISTS {}".format(self._table_refs)
        else:
            print_str = "DROP TABLE {}".format(self._table_refs)
        return print_str

    @property
    def table_refs(self):
        return self._table_refs

    @property
    def if_exists(self):
        return self._if_exists

    def __eq__(self, other):
        if not isinstance(other, DropTableStatement):
            return False
        return self.table_refs == other.table_refs and self.if_exists == other.if_exists

    def __hash__(self) -> int:
        return hash((super().__hash__(), tuple(self.table_refs), self.if_exists))
