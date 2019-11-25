import unittest
from unittest.mock import MagicMock, call

from src.query_parser.eva_ql_parser_visitor import EvaParserVisitor
from third_party.evaQL.parser.frameQLParser import frameQLParser


class ParserVisitorTest(unittest.TestCase):
    def test_should_query_specification_visitor(self):
        EvaParserVisitor.visit = MagicMock()
        mock_visit = EvaParserVisitor.visit
        mock_visit.side_effect = ["target",
                                  {"from": ["from"], "where": "where"}]

        visitor = EvaParserVisitor()
        ctx = MagicMock()
        child_1 = MagicMock()
        child_1.getRuleIndex.return_value = frameQLParser.RULE_selectElements

        child_2 = MagicMock()
        child_2.getRuleIndex.return_value = frameQLParser.RULE_fromClause
        ctx.children = [None, child_1, child_2]

        expected = visitor.visitQuerySpecification(ctx)

        mock_visit.assert_has_calls([call(child_1), call(child_2)])

        self.assertEqual(expected.from_table, "from")
        self.assertEqual(expected.where_clause, "where")
        self.assertEqual(expected.target_list, "target")
