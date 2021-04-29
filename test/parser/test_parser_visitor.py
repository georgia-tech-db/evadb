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
import pandas as pd
import numpy as np

from unittest import mock
from unittest.mock import MagicMock, call

from src.models.storage.batch import Batch
from src.parser.parser_visitor import ParserVisitor
from src.parser.evaql.evaql_parser import evaql_parser
from src.expression.abstract_expression import ExpressionType
from src.expression.function_expression import ExecutionMode
from src.parser.table_ref import TableRef
from antlr4 import TerminalNode


class ParserVisitorTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @mock.patch.object(ParserVisitor, 'visit')
    def test_should_query_specification_visitor(self, mock_visit):
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
        whereExpr = MagicMock()
        ctx.whereExpr = whereExpr
        ctx.tableSources.return_value = tableSources

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
            ExpressionType.INVALID
        )

        ctx.getText.return_value = '='
        self.assertEqual(
            visitor.visitComparisonOperator(ctx),
            ExpressionType.COMPARE_EQUAL
        )

        ctx.getText.return_value = '<'
        self.assertEqual(
            visitor.visitComparisonOperator(ctx),
            ExpressionType.COMPARE_LESSER
        )

        ctx.getText.return_value = '>'
        self.assertEqual(
            visitor.visitComparisonOperator(ctx),
            ExpressionType.COMPARE_GREATER
        )

        ctx.getText.return_value = '@>'
        self.assertEqual(
            visitor.visitComparisonOperator(ctx),
            ExpressionType.COMPARE_CONTAINS
        )

        ctx.getText.return_value = '<@'
        self.assertEqual(
            visitor.visitComparisonOperator(ctx),
            ExpressionType.COMPARE_IS_CONTAINED
        )

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

    @mock.patch.object(ParserVisitor, 'visitChildren')
    def test_visit_string_literal_none(self, mock_visit):
    # def test_visit_string_literal_none(self):
        ''' Testing when string literal is None
            Function: visitStringLiteral
        '''
        visitor = ParserVisitor()
        ctx = MagicMock()
        ctx.STRING_LITERAL.return_value = None

        # ParserVisitor.visitChildren = MagicMock()
        # mock_visit = ParserVisitor.visitChildren

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
            Batch(pd.DataFrame([float(ctx.getText())])))

    def test_visit_int_array_literal(self):
        ''' Testing int array literal
            Function: visitArrayLiteral
        '''
        ctx = MagicMock()
        visitor = ParserVisitor()
        ctx.getText.return_value = '[1,2,3,4]'
        expected = visitor.visitArrayLiteral(ctx)
        self.assertEqual(
            expected.evaluate(),
            Batch(pd.DataFrame({0: [np.array([1, 2, 3, 4])]}))
        )

    def test_visit_str_array_literal(self):
        ''' Testing str array literal
            Function: visitArrayLiteral
        '''
        ctx = MagicMock()
        visitor = ParserVisitor()
        ctx.getText.return_value = "['person', 'car']"
        expected = visitor.visitArrayLiteral(ctx)
        self.assertEqual(
            expected.evaluate(),
            Batch(pd.DataFrame({0: [np.array(['person', 'car'])]}))
        )

    def test_visit_query_specification_base_exception(self):
        ''' Testing Base Exception error handling
            Function: visitQuerySpecification
        '''
        # ParserVisitor.visit = MagicMock()
        # ParserVisitor.visit

        visitor = ParserVisitor()
        ctx = MagicMock()
        child_1 = MagicMock()
        child_2 = MagicMock()
        ctx.children = [None, child_1, child_2]
        child_1.getRuleIndex.side_effect = BaseException

        # expected = visitor.visitQuerySpecification(ctx)

        self.assertRaises(BaseException, visitor.visitQuerySpecification, ctx)


    ##################################################################
    # UDFs
    ##################################################################
    @mock.patch.object(ParserVisitor, 'visit')
    @mock.patch('src.parser.parser_visitor._functions.FunctionExpression')
    def test_visit_udf_function_call(self, func_mock, visit_mock):
        ctx = MagicMock()
        udf_name = 'name'
        udf_output = 'label'
        func_args = [MagicMock(), MagicMock()]
        values = {ctx.simpleId.return_value: udf_name,
                  ctx.functionArgs.return_value: func_args,
                  ctx.dottedId.return_value: udf_output}

        def side_effect(arg):
            return values[arg]

        visit_mock.side_effect = side_effect

        visitor = ParserVisitor()
        actual = visitor.visitUdfFunction(ctx)
        visit_mock.assert_has_calls(
            [call(ctx.simpleId()), call(ctx.dottedId()),
             call(ctx.functionArgs())])

        func_mock.assert_called_with(None, mode=ExecutionMode.EXEC,
                                     name='name', output=udf_output)

        for arg in func_args:
            func_mock.return_value.append_child.assert_any_call(arg)
        self.assertEqual(actual, func_mock.return_value)

    @mock.patch.object(ParserVisitor, 'visit')
    def test_visit_function_args(self, visit_mock):
        ctx = MagicMock()
        obj = MagicMock(spec=TerminalNode())
        ctx.children = ['arg1', obj, 'arg2']
        visit_mock.side_effect = [1, 2]

        visitor = ParserVisitor()
        actual = visitor.visitFunctionArgs(ctx)

        visit_mock.assert_has_calls([call('arg1'), call('arg2')])
        self.assertEqual(actual, [1, 2])

    @mock.patch.object(ParserVisitor, 'visit')
    @mock.patch('src.parser.parser_visitor._functions.CreateUDFStatement')
    def test_visit_create_udf(self, create_udf_mock, visit_mock):
        ctx = MagicMock()
        ctx.children = [MagicMock() for i in range(5)]
        ctx.children[0].getRuleIndex.return_value = evaql_parser.RULE_udfName
        ctx.children[1].getRuleIndex.return_value = evaql_parser. \
            RULE_ifNotExists
        ctx.children[2].getRuleIndex.return_value = evaql_parser. \
            RULE_createDefinitions
        ctx.children[3].getRuleIndex.return_value = evaql_parser.RULE_udfType
        ctx.children[4].getRuleIndex.return_value = evaql_parser.RULE_udfImpl

        ctx.createDefinitions.return_value.__len__.return_value = 2

        udf_name = 'name'
        udf_type = 'classification'
        udf_impl = MagicMock()
        udf_impl.value = 'udf_impl'
        values = {
            ctx.udfName.return_value: udf_name,
            ctx.udfType.return_value: udf_type,
            ctx.udfImpl.return_value: udf_impl,
            ctx.createDefinitions.return_value: 'col'}

        def side_effect(arg):
            return values[arg]

        visit_mock.side_effect = side_effect

        visitor = ParserVisitor()
        actual = visitor.visitCreateUdf(ctx)

        visit_mock.assert_has_calls(
            [call(ctx.udfName()),
             call(ctx.createDefinitions(0)),
             call(ctx.createDefinitions(1)),
             call(ctx.udfType()),
             call(ctx.udfImpl())])

        create_udf_mock.assert_called_once()
        create_udf_mock.assert_called_with(
            udf_name, True, 'col', 'col', 'udf_impl', udf_type)

        self.assertEqual(actual, create_udf_mock.return_value)

    ##################################################################
    # LOAD DATA Statement
    ##################################################################
    @mock.patch.object(ParserVisitor, 'visit')
    @mock.patch('src.parser.parser_visitor._load_statement.LoadDataStatement')
    def test_visit_load_statement(self, mock_load, mock_visit):
        ctx = MagicMock()
        table = 'myVideo'
        path = MagicMock()
        path.value = 'video.mp4'
        params = {ctx.fileName.return_value: path,
                  ctx.tableName.return_value: table}

        def side_effect(arg):
            return params[arg]

        mock_visit.side_effect = side_effect
        visitor = ParserVisitor()
        visitor.visitLoadStatement(ctx)
        mock_visit.assert_has_calls(
            [call(ctx.fileName()), call(ctx.tableName())])
        mock_load.assert_called_once()
        mock_load.assert_called_with(TableRef('myVideo'), 'video.mp4')
