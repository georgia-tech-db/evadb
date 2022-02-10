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

from mock import patch, MagicMock

from eva.optimizer.statement_to_opr_convertor import StatementToPlanConvertor
from eva.parser.select_statement import SelectStatement
from eva.parser.table_ref import TableRef, TableInfo
from eva.parser.create_udf_statement import CreateUDFStatement
from eva.parser.insert_statement import InsertTableStatement
from eva.parser.create_statement import CreateTableStatement
from eva.parser.load_statement import LoadDataStatement
from eva.parser.parser import Parser

from eva.optimizer.operators import (LogicalProject, LogicalGet, LogicalFilter,
                                     LogicalQueryDerivedGet, LogicalCreate,
                                     LogicalCreateUDF, LogicalInsert,
                                     LogicalLoadData, LogicalUnion,
                                     LogicalOrderBy, LogicalLimit,
                                     LogicalSample, LogicalJoin,
                                     LogicalFunctionScan)

from eva.expression.tuple_value_expression import TupleValueExpression
from eva.expression.constant_value_expression import ConstantValueExpression
from eva.expression.comparison_expression import ComparisonExpression
from eva.expression.function_expression import FunctionExpression
from eva.expression.abstract_expression import ExpressionType

from eva.parser.types import ParserOrderBySortType, JoinType


class StatementToOprTest(unittest.TestCase):
    @patch('eva.optimizer.statement_to_opr_convertor.LogicalGet')
    @patch('eva.optimizer.statement_to_opr_convertor.bind_dataset')
    def test_visit_table_ref_should_create_logical_get_opr(self, mock,
                                                           mock_lget):
        converter = StatementToPlanConvertor()
        table_ref = TableRef(TableInfo("test"))
        converter.visit_table_ref(table_ref)
        mock.assert_called_with(table_ref.table)
        mock_lget.assert_called_with(table_ref, mock.return_value)
        self.assertEqual(mock_lget.return_value, converter._plan)

    @patch('eva.optimizer.statement_to_opr_convertor.LogicalGet')
    @patch('eva.optimizer.statement_to_opr_convertor.bind_dataset')
    def test_visit_table_ref_populates_column_mapping(self, mock,
                                                      mock_lget):
        converter = StatementToPlanConvertor()
        converter._populate_column_map = MagicMock()
        table_ref = TableRef(TableInfo("test"))
        converter.visit_table_ref(table_ref)

        converter._populate_column_map.assert_called_with(mock.return_value)

    @patch('eva.optimizer.statement_to_opr_convertor.LogicalFilter')
    @patch('eva.optimizer.statement_to_opr_convertor.bind_predicate_expr')
    def test_visit_select_predicate_should_add_logical_filter(self, mock,
                                                              mock_lfilter):
        converter = StatementToPlanConvertor()
        select_predicate = MagicMock()
        converter._visit_select_predicate(select_predicate)

        mock_lfilter.assert_called_with(select_predicate)
        mock.assert_called_with(select_predicate, converter._column_map)
        mock_lfilter.return_value.append_child.assert_called()
        self.assertEqual(mock_lfilter.return_value, converter._plan)

    @patch('eva.optimizer.statement_to_opr_convertor.LogicalProject')
    @patch('eva.optimizer.statement_to_opr_convertor.bind_columns_expr')
    def test_visit_projection_should_add_logical_predicate(self, mock,
                                                           mock_lproject):
        converter = StatementToPlanConvertor()
        projects = MagicMock()

        converter._visit_projection(projects)

        mock_lproject.assert_called_with(projects)
        mock.assert_called_with(projects, converter._column_map)
        mock_lproject.return_value.append_child.assert_called()
        self.assertEqual(mock_lproject.return_value, converter._plan)

    def test_visit_select_should_call_appropriate_visit_methods(self):
        converter = StatementToPlanConvertor()
        converter.visit_table_ref = MagicMock()
        converter._visit_projection = MagicMock()
        converter._visit_select_predicate = MagicMock()
        converter._visit_union = MagicMock()

        statement = MagicMock()
        statement.from_table = MagicMock(spec=TableRef)
        converter.visit_select(statement)

        converter.visit_table_ref.assert_called_with(statement.from_table)
        converter._visit_projection.assert_called_with(statement.target_list)
        converter._visit_select_predicate.assert_called_with(
            statement.where_clause)

    def test_visit_select_should_not_call_visits_for_null_values(self):
        converter = StatementToPlanConvertor()
        converter.visit_table_ref = MagicMock()
        converter._visit_projection = MagicMock()
        converter._visit_select_predicate = MagicMock()
        converter._visit_union = MagicMock()

        statement = SelectStatement()

        converter.visit_select(statement)

        converter.visit_table_ref.assert_not_called()
        converter._visit_projection.assert_not_called()
        converter._visit_select_predicate.assert_not_called()

    def test_populate_column_map_should_populate_correctly(self):
        converter = StatementToPlanConvertor()
        dataset = MagicMock()
        dataset.columns = [MagicMock() for i in range(5)]
        expected = {}
        for i, column in enumerate(dataset.columns):
            column.name = "NAME" + str(i)
            expected[column.name.lower()] = column

        converter._populate_column_map(dataset)

        self.assertEqual(converter._column_map, expected)

    @patch('eva.optimizer.statement_to_opr_convertor.LogicalCreateUDF')
    @patch('eva.optimizer.\
statement_to_opr_convertor.column_definition_to_udf_io')
    def test_visit_create_udf(self, mock, l_create_udf_mock):
        convertor = StatementToPlanConvertor()
        stmt = MagicMock()
        stmt.name = 'name'
        stmt.if_not_exists = True
        stmt.inputs = ['inp']
        stmt.outputs = ['out']
        stmt.impl_path = 'tmp.py'
        stmt.udf_type = 'classification'
        mock.side_effect = ['inp', 'out']
        convertor.visit_create_udf(stmt)
        mock.assert_any_call(stmt.inputs, True)
        mock.assert_any_call(stmt.outputs, False)
        l_create_udf_mock.assert_called_once()
        l_create_udf_mock.assert_called_with(
            stmt.name,
            stmt.if_not_exists,
            'inp',
            'out',
            stmt.impl_path,
            stmt.udf_type)

    def test_visit_should_call_create_udf(self):
        stmt = MagicMock(spec=CreateUDFStatement)
        convertor = StatementToPlanConvertor()
        mock = MagicMock()
        convertor.visit_create_udf = mock

        convertor.visit(stmt)
        mock.assert_called_once()
        mock.assert_called_with(stmt)

    def test_visit_should_call_insert(self):
        stmt = MagicMock(spec=InsertTableStatement)
        convertor = StatementToPlanConvertor()
        mock = MagicMock()
        convertor.visit_insert = mock

        convertor.visit(stmt)
        mock.assert_called_once()
        mock.assert_called_with(stmt)

    def test_visit_should_call_create(self):
        stmt = MagicMock(spec=CreateTableStatement)
        convertor = StatementToPlanConvertor()
        mock = MagicMock()
        convertor.visit_create = mock

        convertor.visit(stmt)
        mock.assert_called_once()
        mock.assert_called_with(stmt)

    def test_visit_should_call_load_data(self):
        stmt = MagicMock(spec=LoadDataStatement)
        convertor = StatementToPlanConvertor()
        mock = MagicMock()
        convertor.visit_load_data = mock

        convertor.visit(stmt)
        mock.assert_called_once()
        mock.assert_called_with(stmt)

    @patch('eva.optimizer.statement_to_opr_convertor.LogicalLoadData')
    @patch('eva.optimizer.statement_to_opr_convertor.bind_dataset')
    @patch('eva.optimizer.statement_to_opr_convertor.create_video_metadata')
    def test_visit_load_data_when_bind_returns_valid(
            self, mock_create, mock_bind, mock_load):
        mock_bind.return_value = MagicMock()
        table_ref = TableRef(TableInfo("test"))
        stmt = MagicMock(table=table_ref, path='path')
        StatementToPlanConvertor().visit_load_data(stmt)
        mock_bind.assert_called_once_with(table_ref.table)
        mock_load.assert_called_once_with(mock_bind.return_value, 'path')
        mock_create.assert_not_called()

    @patch('eva.optimizer.statement_to_opr_convertor.LogicalLoadData')
    @patch('eva.optimizer.statement_to_opr_convertor.bind_dataset')
    @patch('eva.optimizer.statement_to_opr_convertor.create_video_metadata')
    def test_visit_load_data_when_bind_returns_None(
            self, mock_create, mock_bind, mock_load):
        mock_bind.return_value = None
        table_ref = TableRef(TableInfo("test"))
        stmt = MagicMock(table=table_ref, path='path')
        StatementToPlanConvertor().visit_load_data(stmt)
        mock_create.assert_called_once_with(table_ref.table.table_name)
        mock_bind.assert_called_with(table_ref.table)
        mock_load.assert_called_with(mock_create.return_value, 'path')

    @patch('eva.optimizer.statement_to_opr_convertor.bind_dataset')
    @patch('eva.optimizer.statement_to_opr_convertor.bind_columns_expr')
    @patch('eva.optimizer.statement_to_opr_convertor.bind_predicate_expr')
    def test_should_visit_select_if_nested_query(self, mock_p, mock_c, mock_d):
        m = MagicMock()
        mock_p.return_value = mock_c.return_value = mock_d.return_value = m
        stmt = Parser().parse(""" SELECT id FROM (SELECT data, id FROM video \
            WHERE data > 2) WHERE id>3;""")[0]
        converter = StatementToPlanConvertor()
        actual_plan = converter.visit(stmt)
        plans = [LogicalProject([TupleValueExpression('id')])]
        plans.append(
            LogicalFilter(
                ComparisonExpression(
                    ExpressionType.COMPARE_GREATER,
                    TupleValueExpression('id'),
                    ConstantValueExpression(3))))
        plans.append(LogicalQueryDerivedGet())
        plans.append(LogicalProject(
            [TupleValueExpression('data'), TupleValueExpression('id')]))
        plans.append(
            LogicalFilter(
                ComparisonExpression(
                    ExpressionType.COMPARE_GREATER,
                    TupleValueExpression('data'),
                    ConstantValueExpression(2))))

        plans.append(LogicalGet(TableRef(TableInfo('video')), m))
        expected_plan = None
        for plan in reversed(plans):
            if expected_plan:
                plan.append_child(expected_plan),

            expected_plan = plan
        self.assertEqual(expected_plan, actual_plan)
        wrong_plan = plans[0]
        for plan in plans[1:]:
            wrong_plan.append_child(plan)
        self.assertNotEqual(wrong_plan, actual_plan)

    @patch('eva.optimizer.statement_to_opr_convertor.bind_dataset')
    @patch('eva.optimizer.statement_to_opr_convertor.bind_columns_expr')
    @patch('eva.optimizer.statement_to_opr_convertor.bind_predicate_expr')
    def test_visit_select_orderby(self, mock_p, mock_c, mock_d):
        m = MagicMock()
        mock_p.return_value = mock_c.return_value = mock_d.return_value = m
        stmt = Parser().parse(""" SELECT data, id FROM video \
            WHERE data > 2 ORDER BY data, id DESC;""")[0]

        converter = StatementToPlanConvertor()
        actual_plan = converter.visit(stmt)
        plans = []

        plans.append(LogicalOrderBy(
            [(TupleValueExpression('data'), ParserOrderBySortType.ASC),
             (TupleValueExpression('id'), ParserOrderBySortType.DESC)]))

        plans.append(LogicalProject(
            [TupleValueExpression('data'), TupleValueExpression('id')]))

        plans.append(
            LogicalFilter(
                ComparisonExpression(
                    ExpressionType.COMPARE_GREATER,
                    TupleValueExpression('data'),
                    ConstantValueExpression(2))))

        plans.append(LogicalGet(TableRef(TableInfo('video')), m))

        expected_plan = None
        for plan in reversed(plans):
            if expected_plan:
                plan.append_child(expected_plan)
            expected_plan = plan

        self.assertEqual(expected_plan, actual_plan)

        wrong_plan = plans[0]
        for plan in plans[1:]:
            wrong_plan.append_child(plan)
        self.assertNotEqual(wrong_plan, actual_plan)

    @patch('eva.optimizer.statement_to_opr_convertor.bind_dataset')
    @patch('eva.optimizer.statement_to_opr_convertor.bind_columns_expr')
    @patch('eva.optimizer.statement_to_opr_convertor.bind_predicate_expr')
    def test_visit_select_limit(self, mock_p, mock_c, mock_d):
        m = MagicMock()
        mock_p.return_value = mock_c.return_value = mock_d.return_value = m
        stmt = Parser().parse(""" SELECT data, id FROM video \
                   WHERE data > 2 LIMIT 3;""")[0]

        converter = StatementToPlanConvertor()
        actual_plan = converter.visit(stmt)
        plans = []

        plans.append(LogicalLimit(ConstantValueExpression(3)))

        plans.append(LogicalProject(
            [TupleValueExpression('data'), TupleValueExpression('id')]))

        plans.append(
            LogicalFilter(
                ComparisonExpression(
                    ExpressionType.COMPARE_GREATER,
                    TupleValueExpression('data'),
                    ConstantValueExpression(2))))

        plans.append(LogicalGet(TableRef(TableInfo('video')), m))

        expected_plan = None
        for plan in reversed(plans):
            if expected_plan:
                plan.append_child(expected_plan)
            expected_plan = plan

        self.assertEqual(expected_plan, actual_plan)

        wrong_plan = plans[0]
        for plan in plans[1:]:
            wrong_plan.append_child(plan)
        self.assertNotEqual(wrong_plan, actual_plan)

    @patch('eva.optimizer.statement_to_opr_convertor.bind_dataset')
    @patch('eva.optimizer.statement_to_opr_convertor.bind_columns_expr')
    @patch('eva.optimizer.statement_to_opr_convertor.bind_predicate_expr')
    def test_visit_select_sample(self, mock_p, mock_c, mock_d):
        m = MagicMock()
        mock_p.return_value = mock_c.return_value = mock_d.return_value = m
        stmt = Parser().parse(""" SELECT data, id FROM video SAMPLE 2 \
                   WHERE id > 2 LIMIT 3;""")[0]

        converter = StatementToPlanConvertor()
        actual_plan = converter.visit(stmt)
        plans = []

        plans.append(LogicalLimit(ConstantValueExpression(3)))

        plans.append(LogicalProject(
            [TupleValueExpression('data'), TupleValueExpression('id')]))

        plans.append(
            LogicalFilter(
                ComparisonExpression(
                    ExpressionType.COMPARE_GREATER,
                    TupleValueExpression('id'),
                    ConstantValueExpression(2))))

        plans.append(LogicalSample(ConstantValueExpression(2)))

        plans.append(LogicalGet(TableRef(TableInfo('video'),
                                         ConstantValueExpression(2)), m))

        expected_plan = None
        for plan in reversed(plans):
            if expected_plan:
                plan.append_child(expected_plan)
            expected_plan = plan

        self.assertEqual(expected_plan, actual_plan)

    @patch('eva.optimizer.statement_to_opr_convertor.bind_dataset')
    @patch('eva.optimizer.statement_to_opr_convertor.bind_columns_expr')
    @patch('eva.optimizer.statement_to_opr_convertor.bind_predicate_expr')
    def test_should_visit_select_union_if_union_query(self, mock_p, mock_c,
                                                      mock_d):
        m = MagicMock()
        mock_p.return_value = mock_c.return_value = mock_d.return_value = m
        stmt = Parser().parse(""" SELECT id FROM video WHERE id>3
                              UNION ALL
                              SELECT id FROM video WHERE id<=3;""")[0]
        converter = StatementToPlanConvertor()
        actual_plan = converter.visit(stmt)
        left_plans = [LogicalProject([TupleValueExpression('id')])]
        left_plans.append(
            LogicalFilter(
                ComparisonExpression(
                    ExpressionType.COMPARE_GREATER,
                    TupleValueExpression('id'),
                    ConstantValueExpression(3))))
        left_plans.append(LogicalGet(TableRef(TableInfo('video')), m))

        def reverse_plan(plans):
            return_plan = None
            for plan in reversed(plans):
                if return_plan:
                    plan.append_child(return_plan)
                return_plan = plan
            return return_plan
        expect_left_plan = reverse_plan(left_plans)

        right_plans = [LogicalProject([TupleValueExpression('id')])]
        right_plans.append(
            LogicalFilter(
                ComparisonExpression(
                    ExpressionType.COMPARE_LEQ,
                    TupleValueExpression('id'),
                    ConstantValueExpression(3))))
        right_plans.append(LogicalGet(TableRef(TableInfo('video')), m))
        expect_right_plan = reverse_plan(right_plans)
        expected_plan = LogicalUnion(True)
        expected_plan.append_child(expect_right_plan)
        expected_plan.append_child(expect_left_plan)

        self.assertEqual(expected_plan, actual_plan)

    def test_should_return_false_for_unequal_plans(self):
        create_plan = LogicalCreate(
            TableRef(TableInfo('video')), [MagicMock()])
        create_udf_plan = LogicalCreateUDF('udf', False, None, None, None)
        insert_plan = LogicalInsert(
            MagicMock(), 0, [
                MagicMock()], [
                MagicMock()])
        query_derived_plan = LogicalQueryDerivedGet()
        load_plan = LogicalLoadData(MagicMock(), MagicMock())
        self.assertEqual(create_plan, create_plan)
        self.assertEqual(create_udf_plan, create_udf_plan)
        self.assertNotEqual(create_plan, create_udf_plan)
        self.assertNotEqual(create_udf_plan, create_plan)
        create_plan.append_child(create_udf_plan)
        self.assertNotEqual(create_plan, create_udf_plan)
        self.assertNotEqual(query_derived_plan, create_plan)
        self.assertNotEqual(insert_plan, query_derived_plan)
        self.assertNotEqual(load_plan, insert_plan)

    @patch('eva.optimizer.statement_to_opr_convertor.bind_dataset')
    @patch('eva.optimizer.statement_to_opr_convertor.bind_columns_expr')
    @patch('eva.optimizer.statement_to_opr_convertor.bind_predicate_expr')
    def test_should_handle_lateral_join(self, mock_p, mock_c, mock_d):
        m = MagicMock()
        mock_p.return_value = mock_c.return_value = mock_d.return_value = m
        stmt = Parser().parse("""SELECT id FROM DETRAC,
                LATERAL UNNEST(ObjDet(frame)) WHERE id > 3;""")[0]
        converter = StatementToPlanConvertor()
        actual_plan = converter.visit(stmt)

        right = FunctionExpression(func=None, name='UNNEST')
        child = FunctionExpression(func=None, name='ObjDet')
        child.append_child(TupleValueExpression('frame'))
        right.append_child(child)
        left = LogicalGet(TableRef(TableInfo('DETRAC')), m)
        join = LogicalJoin(JoinType.LATERAL_JOIN)
        join.append_child(left)
        join.append_child(LogicalFunctionScan(right))
        filter = LogicalFilter(
            ComparisonExpression(
                ExpressionType.COMPARE_GREATER,
                TupleValueExpression('id'),
                ConstantValueExpression(3)))
        filter.append_child(join)
        expected_plan = LogicalProject([TupleValueExpression('id')])
        expected_plan.append_child(filter)
        self.assertEqual(actual_plan, expected_plan)


if __name__ == '__main__':
    unittest.main()
