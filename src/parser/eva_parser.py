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

from antlr4 import InputStream, CommonTokenStream

from src.parser.evaql.parser.frameQLParser import frameQLParser
from src.parser.evaql.parser.frameQLLexer import frameQLLexer
from src.parser.eva_ql_parser_visitor import EvaParserVisitor

class EvaFrameQLParser():
    """
    Parser for eva; based on frameQL grammar
    """

    def __init__(self):
        self._visitor = EvaParserVisitor()

    def parse(self, query_string: str) -> list:
        lexer = frameQLLexer(InputStream(query_string))
        stream = CommonTokenStream(lexer)
        parser = frameQLParser(stream)
        tree = parser.root()
        return self._visitor.visit(tree)
