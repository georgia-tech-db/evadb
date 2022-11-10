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
from eva.parser.statement import AbstractStatement
from eva.parser.types import StatementType


class ExplainStatement(AbstractStatement):
    def __init__(self, explainable_stmt: AbstractStatement):
        super().__init__(StatementType.EXPLAIN)
        self._explainable_stmt = explainable_stmt

    def __str__(self) -> str:
        print_str = "EXPLAIN {}".format(str(self._explainable_stmt))
        return print_str

    @property
    def explainable_stmt(self) -> AbstractStatement:
        return self._explainable_stmt

    def __eq__(self, other):
        if not isinstance(other, ExplainStatement):
            return False
        return self._explainable_stmt == other.explainable_stmt

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.explainable_stmt))
