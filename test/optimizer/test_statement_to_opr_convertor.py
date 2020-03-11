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

from src.optimizer.statement_to_opr_convertor import StatementToPlanConvertor
from src.parser.select_statement import SelectStatement
from src.parser.table_ref import TableRef, TableInfo


class StatementToOprTest(unittest.TestCase):
    @patch('src.optimizer.statement_to_opr_convertor.LogicalGet')
    @patch('src.optimizer.statement_to_opr_convertor.bind_dataset')
    def test_visit_table_ref_should_create_logical_get_opr(self, mock,
                                                           mock_lget):
        converter = StatementToPlanConvertor()
        table_ref = TableRef(TableInfo("test"))
        converter.visit_table_ref(table_ref)
        mock.assert_called_with(table_ref.table_info)
        mock_lget.assert_called_with(table_ref, mock.return_value)
        self.assertEqual(mock_lget.return_value, converter._plan)

    @patch('src.optimizer.statement_to_opr_convertor.LogicalGet')
    @patch('src.optimizer.statement_to_opr_convertor.bind_dataset')
    def test_visit_table_ref_populates_column_mapping(self, mock,
                                                      mock_lget):
        converter = StatementToPlanConvertor()
        converter._populate_column_map = MagicMock()
        table_ref = TableRef(TableInfo("test"))
        converter.visit_table_ref(table_ref)

        converter._populate_column_map.assert_called_with(mock.return_value)

    @patch('src.optimizer.statement_to_opr_convertor.LogicalFilter')
    @patch('src.optimizer.statement_to_opr_convertor.bind_predicate_expr')
    def test_visit_select_predicate_should_add_logical_filter(self, mock,
                                                              mock_lfilter):
        converter = StatementToPlanConvertor()
        select_predicate = MagicMock()
        converter._visit_select_predicate(select_predicate)

        mock_lfilter.assert_called_with(select_predicate)
        mock.assert_called_with(select_predicate, converter._column_map)
        mock_lfilter.return_value.append_child.assert_called()
        self.assertEqual(mock_lfilter.return_value, converter._plan)

    @patch('src.optimizer.statement_to_opr_convertor.LogicalProject')
    @patch('src.optimizer.statement_to_opr_convertor.bind_columns_expr')
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

        statement = MagicMock()

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
