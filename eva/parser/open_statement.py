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

from eva.parser.statement import AbstractStatement
from eva.parser.types import StatementType


class OpenStatement(AbstractStatement):
    def __init__(self, path: str):
        super().__init__(StatementType.OPEN)
        self._path = Path(path)

    @property
    def path(self):
        return self._path

    def __str__(self) -> str:
        print_str = "OPEN {}".format(self._path)
        return print_str

    def __eq__(self, other):
        if not isinstance(other, OpenStatement):
            return False
        return self._path == other.path

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.path))
