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

import unittest

from unittest import mock
from unittest.mock import MagicMock, call

from src.parser.parser_visitor import ParserVisitor
from src.parser.evaql.evaql_parser import evaql_parser
from src.expression.abstract_expression import ExpressionType


class ParserVisitorTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_should_query_specification_visitor(self):
        ParserVisitor.visit = MagicMock()
        mock_visit = ParserVisitor.visit
        mock_visit.side_effect = ["columns",
                                  {"from": ["tables"], "where": "predicates"}]

        visitor = ParserVisitor()
        ctx = MagicMock()
        child_1 = MagicMock()
        child_1.getRuleIndex.return_value = evaql_parser.RULE_selectElements

        child_2 = MagicMock()
        child_2.getRuleIndex.return_value = evaql_parser.RULE_fromClause
        ctx.children = [None, child_1, child_2]

        expected = visitor.visitQuerySpecification(ctx)

        mock_visit.assert_has_calls([call(child_1), call(child_2)])

        self.assertEqual(expected.from_table, "tables")
        self.assertEqual(expected.where_clause, "predicates")
        self.assertEqual(expected.target_list, "columns")

    @mock.patch.object(ParserVisitor, 'visit')
    def test_from_clause_visitor(self, mock_visit):
        mock_visit.side_effect = ["tables", "predicates"]

        ctx = MagicMock()
        tableSources = MagicMock()
        ctx.tableSources.return_value = tableSources
        whereExpr = MagicMock()
        ctx.whereExpr = whereExpr

        visitor = ParserVisitor()
        expected = visitor.visitFromClause(ctx)
        mock_visit.assert_has_calls([call(tableSources), call(whereExpr)])

        self.assertEqual(expected.get('where'), 'predicates')
        self.assertEqual(expected.get('from'), 'tables')

    def test_logical_operator(self):
        ctx = MagicMock()
        visitor = ParserVisitor()

        self.assertEqual(
            visitor.visitLogicalOperator(ctx),
            ExpressionType.INVALID)

        ctx.getText.return_value = 'OR'
        self.assertEqual(
            visitor.visitLogicalOperator(ctx),
            ExpressionType.LOGICAL_OR)

        ctx.getText.return_value = 'AND'
        self.assertEqual(
            visitor.visitLogicalOperator(ctx),
            ExpressionType.LOGICAL_AND)

    def test_comparison_operator(self):
        ctx = MagicMock()
        visitor = ParserVisitor()

        self.assertEqual(
            visitor.visitComparisonOperator(ctx),
            ExpressionType.INVALID)

        ctx.getText.return_value = '='
        self.assertEqual(
            visitor.visitComparisonOperator(ctx),
            ExpressionType.COMPARE_EQUAL)

        ctx.getText.return_value = '<'
        self.assertEqual(
            visitor.visitComparisonOperator(ctx),
            ExpressionType.COMPARE_LESSER)

        ctx.getText.return_value = '>'
        self.assertEqual(
            visitor.visitComparisonOperator(ctx),
            ExpressionType.COMPARE_GREATER)

    # To be fixed
    # def test_visit_full_column_name_none(self):
    #    ''' Testing for getting a Warning when column name is None
    #        Function: visitFullColumnName
    #    '''
    #    ctx = MagicMock()
    #    visitor = ParserVisitor()
    #    ParserVisitor.visit = MagicMock()
    #    ParserVisitor.visit.return_value = None
    #    with self.assertWarns(SyntaxWarning, msg='Column Name Missing'):
    #        visitor.visitFullColumnName(ctx)

    # def test_visit_table_name_none(self):
    #    ''' Testing for getting a Warning when table name is None
    #        Function: visitTableName
    #    '''
    #    ctx = MagicMock()
    #    visitor = ParserVisitor()
    #    ParserVisitor.visit = MagicMock()
    #    ParserVisitor.visit.return_value = None
    #    with self.assertWarns(SyntaxWarning, msg='Invalid from table'):
    #        visitor.visitTableName(ctx)

    def test_logical_expression(self):
        ''' Testing for break in code if len(children) < 3
            Function : visitLogicalExpression
        '''
        ctx = MagicMock()
        visitor = ParserVisitor()

        # Test for no children
        ctx.children = []
        expected = visitor.visitLogicalExpression(ctx)
        self.assertEqual(expected, None)

        # Test for one children
        child_1 = MagicMock()
        ctx.children = [child_1]
        expected = visitor.visitLogicalExpression(ctx)
        self.assertEqual(expected, None)

        # Test for two children
        child_1 = MagicMock()
        child_2 = MagicMock()
        ctx.children = [child_1, child_2]
        expected = visitor.visitLogicalExpression(ctx)
        self.assertEqual(expected, None)

    def test_visit_string_literal_none(self):
        ''' Testing when string literal is None
            Function: visitStringLiteral
        '''
        visitor = ParserVisitor()
        ctx = MagicMock()
        ctx.STRING_LITERAL.return_value = None

        ParserVisitor.visitChildren = MagicMock()
        mock_visit = ParserVisitor.visitChildren

        visitor.visitStringLiteral(ctx)
        mock_visit.assert_has_calls([call(ctx)])

    def test_visit_constant(self):
        ''' Testing for value of returned constant
            when real literal is not None
            Function: visitConstant
        '''
        ctx = MagicMock()
        visitor = ParserVisitor()
        ctx.REAL_LITERAL.return_value = '5'
        expected = visitor.visitConstant(ctx)
        self.assertEqual(
            expected.evaluate(),
            float(ctx.getText()))

    def test_visit_query_specification_base_exception(self):
        ''' Testing Base Exception error handling
            Function: visitQuerySpecification
        '''
        ParserVisitor.visit = MagicMock()
        ParserVisitor.visit

        visitor = ParserVisitor()
        ctx = MagicMock()
        child_1 = MagicMock()
        child_2 = MagicMock()
        ctx.children = [None, child_1, child_2]
        child_1.getRuleIndex.side_effect = BaseException()

        expected = visitor.visitQuerySpecification(ctx)

        self.assertEqual(expected, None)

    ##################################################################
    # UDFs
    ##################################################################

    def test_visit_udf_function_call(self):
        parser = Parser()
        select_query = "SELECT FastRCNN(data) From TAIPAI \
            WHERE FastRCNN(data).label = 'car';"
        eva_statement_list = parser.parse(select_query)
        

if __name__ == '__main__':
    unittest.main()
