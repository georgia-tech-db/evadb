import sys
from antlr4 import InputStream, CommonTokenStream
from third_party.evaQL.parser.frameQLParser import frameQLParser 
from third_party.evaQL.parser.frameQLLexer import frameQLLexer
from src.query_parser.eva_ql_parser_visitor import EvaParserVisitor
from src.query_parser.eva_statement import EvaStatementList


class EvaFrameQLParser():
    def build_eva_parse_tree(self, query_string: str) -> EvaStatementList:    
        lexer = frameQLLexer(InputStream(query_string))
        stream = CommonTokenStream(lexer)
        parser = frameQLParser(stream)
        tree = parser.root()
        visitor = EvaParserVisitor()
        return visitor.visit(tree)
        # print(tree.toStringTree(recog=parser))
