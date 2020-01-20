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

from src.parser.evaql.evaql_parser import evaql_parser
from src.parser.evaql.evaql_lexer import evaql_lexer

from src.parser.evaql_parser_visitor import EvaQLParserVisitor


class EvaQLParser(object):
    """
    Parser for eva; based on EVAQL grammar
    """
    _instance = None
    _visitor = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EvaQLParser, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._visitor = EvaQLParserVisitor()

    def parse(self, query_string: str) -> list:
        lexer = evaql_lexer(InputStream(query_string))
        stream = CommonTokenStream(lexer)
        parser = evaql_parser(stream)
        tree = parser.root()
        return self._visitor.visit(tree)
