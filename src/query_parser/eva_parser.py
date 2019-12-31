import sys
from antlr4 import InputStream, CommonTokenStream
from third_party.evaQL.parser.frameQLParser import frameQLParser
from third_party.evaQL.parser.frameQLLexer import frameQLLexer
from src.query_parser.eva_ql_parser_visitor import EvaParserVisitor


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
