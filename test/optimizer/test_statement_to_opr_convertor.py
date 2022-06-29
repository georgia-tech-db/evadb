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
from eva.parser.rename_statement import RenameTableStatement
from eva.parser.truncate_statement import TruncateTableStatement
from eva.parser.drop_statement import DropTableStatement
from eva.parser.create_statement import CreateTableStatement
from eva.optimizer.operators import (LogicalQueryDerivedGet, LogicalCreate,
                                     LogicalCreateUDF, LogicalInsert,
                                     LogicalLoadData)


class StatementToOprTest(unittest.TestCase):
    @patch('eva.optimizer.statement_to_opr_convertor.LogicalGet')
    def test_visit_table_ref_should_create_logical_get_opr(self,
                                                           mock_lget):
        converter = StatementToPlanConvertor()
        table_ref = MagicMock(spec=TableRef, alias='alias')
        table_ref.is_select.return_value = False
        table_ref.sample_freq = None
        converter.visit_table_ref(table_ref)
        mock_lget.assert_called_with(table_ref,
                                     table_ref.table.table_obj,
                                     'alias')
        self.assertEqual(mock_lget.return_value, converter._plan)

    @patch('eva.optimizer.statement_to_opr_convertor.LogicalFilter')
    def test_visit_select_predicate_should_add_logical_filter(self,
                                                              mock_lfilter):
        converter = StatementToPlanConvertor()
        select_predicate = MagicMock()
        converter._visit_select_predicate(select_predicate)

        mock_lfilter.assert_called_with(select_predicate)
        mock_lfilter.return_value.append_child.assert_called()
        self.assertEqual(mock_lfilter.return_value, converter._plan)

    @patch('eva.optimizer.statement_to_opr_convertor.LogicalProject')
    def test_visit_projection_should_add_logical_predicate(self,
                                                           mock_lproject):
        converter = StatementToPlanConvertor()
        projects = MagicMock()

        converter._visit_projection(projects)
        mock_lproject.assert_called_with(projects)
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

    # Modified
    def test_visit_should_call_rename(self):
        stmt = MagicMock(spec=RenameTableStatement)
        convertor = StatementToPlanConvertor()
        mock = MagicMock()
        convertor.visit_rename = mock

        convertor.visit(stmt)
        mock.assert_called_once()
        mock.assert_called_with(stmt)

    def test_visit_should_call_truncate(self):
        stmt = MagicMock(spec=TruncateTableStatement)
        convertor = StatementToPlanConvertor()
        mock = MagicMock()
        convertor.visit_truncate = mock

        convertor.visit(stmt)
        mock.assert_called_once()
        mock.assert_called_with(stmt)

    def test_visit_should_call_drop(self):
        stmt = MagicMock(spec=DropTableStatement)
        convertor = StatementToPlanConvertor()
        mock = MagicMock()
        convertor.visit_drop = mock
        convertor.visit(stmt)
        mock.assert_called_once()
        mock.assert_called_with(stmt)

    def test_should_return_false_for_unequal_plans(self):
        create_plan = LogicalCreate(
            TableRef(TableInfo('video')), [MagicMock()])
        create_udf_plan = LogicalCreateUDF('udf', False, None, None, None)
        insert_plan = LogicalInsert(
            MagicMock(), 0, [
                MagicMock()], [
                MagicMock()])
        query_derived_plan = LogicalQueryDerivedGet(alias='T')
        load_plan = LogicalLoadData(MagicMock(), MagicMock(),
                                    MagicMock(), MagicMock())
        self.assertEqual(create_plan, create_plan)
        self.assertEqual(create_udf_plan, create_udf_plan)
        self.assertNotEqual(create_plan, create_udf_plan)
        self.assertNotEqual(create_udf_plan, create_plan)
        create_plan.append_child(create_udf_plan)
        self.assertNotEqual(create_plan, create_udf_plan)
        self.assertNotEqual(query_derived_plan, create_plan)
        self.assertNotEqual(insert_plan, query_derived_plan)
        self.assertNotEqual(load_plan, insert_plan)
