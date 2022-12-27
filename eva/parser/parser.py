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
from pprint import pprint

from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener
from deepdiff import DeepDiff

from eva.parser.evaql.evaql_lexer import evaql_lexer
from eva.parser.evaql.evaql_parser import evaql_parser
from eva.parser.lark_parser import LarkParser
from eva.parser.parser_visitor import ParserVisitor


class AntlrErrorListener(ErrorListener):

    # Reference
    # https://www.antlr.org/api/Java/org/antlr/v4/runtime/BaseErrorListener.html

    def __init__(self):
        super(AntlrErrorListener, self).__init__()

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error_str = (
            "ERROR: Syntax error - Line"
            + str(line)
            + ": Col "
            + str(column)
            + " - "
            + str(msg)
        )
        raise Exception(error_str)

    # def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex,
    #                    exact, ambigAlts, configs):
    #    error_str = "ERROR: Ambiguity -" + str(configs)
    #    raise Exception(error_str)

    # def reportAttemptingFullContext(self, recognizer, dfa, startIndex,
    #                                 stopIndex, conflictingAlts, configs):
    #     error_str = "ERROR: Attempting Full Context -" + str(configs)
    #     raise Exception(error_str)

    # def reportContextSensitivity(self, recognizer, dfa, startIndex,
    #                              stopIndex, prediction, configs):
    #     error_str = "ERROR: Context Sensitivity -" + str(configs)
    #     raise Exception(error_str)


class Parser(object):
    """
    Parser for eva; based on EVAQL grammar
    """

    _instance = None
    _visitor = None
    _error_listener = None
    _lark_parser = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Parser, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._visitor = ParserVisitor()
        self._error_listener = AntlrErrorListener()
        self._lark_parser = LarkParser()

    def parse(self, query_string: str) -> list:
        lexer = evaql_lexer(InputStream(query_string))
        stream = CommonTokenStream(lexer)

        parser = evaql_parser(stream)
        # Attach error listener for debugging parser errors
        parser._listeners = [self._error_listener]

        tree = parser.root()

        # Call lark
        lark_output = self._lark_parser.parse(query_string)
        antlr_output = self._visitor.visit(tree)
        verbose_diff = False

        if lark_output != antlr_output:
            pprint("Different parse trees: ")
            pprint(query_string)
            if verbose_diff is True:
                pprint("--------  LARK  --------")
                pprint(lark_output[0].__str__())
                pprint("-------- ANTLR  --------")
                pprint(antlr_output[0].__str__())
                pprint("-------- DDIFF  --------")
                d = DeepDiff(lark_output[0], antlr_output[0])
                pprint(d)
        elif verbose_diff is True:
            pprint("Identical parse trees")

        return lark_output
