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
from eva.expression.abstract_expression import AbstractExpression
from eva.parser.statement import AbstractStatement
from eva.parser.select_statement import SelectStatement
from eva.parser.types import StatementType


class SemanticStatement(AbstractStatement):
    """Semantic Statement constructed after parsing the input query

    Attributes:
        _semantic_text: the original sematnci search query
        SelectStatement : the corresponding select statement on the low level
    """

    def __init__(
        self,
        semantic_text: str,
        select_statement: SelectStatement,
    ):
        super().__init__(StatementType.SEMANTIC)
        self._semantic_text = semantic_text.strip('\"')
        self._select_statement = select_statement

    def __str__(self) -> str:
        return 'SEMANTIC "{text}";' .format(text=self._semantic_text)

    @property
    def semantic_text(self):
        return self._semantic_text

    @property
    def select_statement(self):
        return self._select_statement
    
    @select_statement.setter
    def select_statement(self, stmt):
        self.select_statement = stmt

    def __eq__(self, other):
        if not isinstance(other, SemanticStatement):
            return False
        return self._select_statement == other._select_statement

    def __hash__(self) -> int:
        return hash((super().__hash__(), self._semantic_text, self._select_statement))
