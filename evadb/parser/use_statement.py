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
from __future__ import annotations

from evadb.parser.statement import AbstractStatement
from evadb.parser.types import StatementType


class UseStatement(AbstractStatement):
    def __init__(self, database_name: str, query_string: str):
        super().__init__(StatementType.USE)
        self._database_name = database_name
        self._query_string = query_string

    @property
    def database_name(self):
        return self._database_name

    @property
    def query_string(self):
        return self._query_string

    def __str__(self):
        return f"USE {self.database_name} ({self.query_string})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UseStatement):
            return False
        return (
            self.database_name == other.database_name
            and self.query_string == other.query_string
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.database_name,
                self.query_string,
            )
        )
