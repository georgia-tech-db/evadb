# coding=utf-8
# Copyright 2018-2023 EvaDB
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
from unittest.mock import MagicMock, patch

from evadb.binder.binder_utils import BinderError
from evadb.binder.statement_binder import StatementBinder
from evadb.binder.statement_binder_context import StatementBinderContext
from evadb.catalog.catalog_type import NdArrayType
from evadb.expression.tuple_value_expression import TupleValueExpression
from evadb.parser.alias import Alias
from evadb.parser.create_statement import ColumnDefinition


class StatementBinderTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_bind_tuple_value_expression(self):
        with patch.object(StatementBinderContext, "get_binded_column") as mock:
            mock.return_value = ["table_alias", "col_obj"]
            binder = StatementBinder(StatementBinderContext(MagicMock()))
            tve = MagicMock()
            tve.col_name = "col_name"
            binder._bind_tuple_expr(tve)
            col_alias = "{}.{}".format("table_alias", "col_name")
            mock.assert_called_once()
            self.assertEqual(tve.col_object, "col_obj")
            self.assertEqual(tve.col_alias, col_alias)

    @patch("evadb.binder.statement_binder.bind_table_info")
    def test_bind_tableref(self, mock_bind_table_info):
        with patch.object(StatementBinderContext, "add_table_alias") as mock:
            catalog = MagicMock()
            binder = StatementBinder(StatementBinderContext(catalog))
            tableref = MagicMock()
            tableref.is_table_atom.return_value = True
            binder._bind_tableref(tableref)
            mock.assert_called_with(
                tableref.alias.alias_name, tableref.table.table_name
            )
            mock_bind_table_info.assert_called_once_with(catalog(), tableref.table)

        with patch.object(StatementBinder, "bind") as mock_binder:
            with patch.object(
                StatementBinderContext, "add_derived_table_alias"
            ) as mock_context:
                binder = StatementBinder(StatementBinderContext(MagicMock()))
                tableref = MagicMock()
                tableref.is_table_atom.return_value = False
                tableref.is_select.return_value = True
                binder._bind_tableref(tableref)
                mock_context.assert_called_with(
                    tableref.alias.alias_name,
                    tableref.select_statement.target_list,
                )
                mock_binder.assert_called_with(tableref.select_statement)

    def test_bind_tableref_with_func_expr(self):
        with patch.object(StatementBinder, "bind") as mock_binder:
            binder = StatementBinder(StatementBinderContext(MagicMock()))
            tableref = MagicMock()
            tableref.is_table_atom.return_value = False
            tableref.is_select.return_value = False
            tableref.is_join.return_value = False
            binder._bind_tableref(tableref)
            mock_binder.assert_called_with(tableref.table_valued_expr.func_expr)

    def test_bind_tableref_with_join(self):
        with patch.object(StatementBinder, "bind") as mock_binder:
            binder = StatementBinder(StatementBinderContext(MagicMock()))
            tableref = MagicMock()
            tableref.is_table_atom.return_value = False
            tableref.is_select.return_value = False
            tableref.is_join.return_value = True
            binder._bind_tableref(tableref)
            mock_binder.assert_any_call(tableref.join_node.left)
            mock_binder.assert_any_call(tableref.join_node.right)

    def test_bind_tableref_should_raise(self):
        with patch.object(StatementBinder, "bind"):
            with self.assertRaises(BinderError):
                binder = StatementBinder(StatementBinderContext(MagicMock()))
                tableref = MagicMock()
                tableref.is_select.return_value = False
                tableref.is_table_valued_expr.return_value = False
                tableref.is_join.return_value = False
                tableref.is_table_atom.return_value = False
                binder._bind_tableref(tableref)

    @patch("evadb.binder.statement_binder.StatementBinderContext")
    def test_bind_tableref_starts_new_context(self, mock_ctx):
        with patch.object(StatementBinder, "bind"):
            binder = StatementBinder(StatementBinderContext(MagicMock()))
            tableref = MagicMock()
            tableref.is_table_atom.return_value = False
            tableref.is_join.return_value = False
            tableref.is_select.return_value = True
            binder._bind_tableref(tableref)
            self.assertEqual(mock_ctx.call_count, 1)

    def test_bind_create_mat_statement(self):
        with patch.object(StatementBinder, "bind") as mock_binder:
            binder = StatementBinder(StatementBinderContext(MagicMock()))
            mat_statement = MagicMock()
            binder._bind_create_mat_statement(mat_statement)
            mock_binder.assert_called_with(mat_statement.query)

    def test_raises_mismatch_columns_create_mat_statement(self):
        with patch.object(StatementBinder, "bind"):
            binder = StatementBinder(StatementBinderContext(MagicMock()))
            mat_statement = MagicMock()
            mat_statement.col_list = [ColumnDefinition("id", None, None, None)]
            mat_statement.query.target_list = [
                TupleValueExpression(col_name="id"),
                TupleValueExpression(col_name="label"),
            ]
            with self.assertRaises(
                Exception, msg="Projected columns mismatch, expected 1 found 2."
            ):
                binder._bind_create_mat_statement(mat_statement)

    def test_bind_explain_statement(self):
        with patch.object(StatementBinder, "bind") as mock_binder:
            binder = StatementBinder(StatementBinderContext(MagicMock()))
            stmt = MagicMock()
            binder._bind_explain_statement(stmt)
            mock_binder.assert_called_with(stmt.explainable_stmt)

    @patch("evadb.binder.statement_binder.load_udf_class_from_file")
    @patch("evadb.binder.statement_binder.get_file_checksum")
    def test_bind_func_expr(
        self, mock_get_file_checksum, mock_load_udf_class_from_file
    ):
        # setup
        func_expr = MagicMock(
            name="func_expr", alias=Alias("func_expr"), output_col_aliases=[]
        )
        func_expr.name.lower.return_value = "func_expr"
        obj1 = MagicMock()
        obj1.name.lower.return_value = "out1"
        obj2 = MagicMock()
        obj2.name.lower.return_value = "out2"
        func_output_objs = [obj1, obj2]
        udf_obj = MagicMock()

        mock_catalog = MagicMock()
        mock_get_name = mock_catalog().get_udf_catalog_entry_by_name = MagicMock()
        mock_get_name.return_value = udf_obj

        mock_get_udf_outputs = (
            mock_catalog().get_udf_io_catalog_output_entries
        ) = MagicMock()
        mock_get_udf_outputs.return_value = func_output_objs
        mock_load_udf_class_from_file.return_value.return_value = (
            "load_udf_class_from_file"
        )
        mock_get_file_checksum.return_value = udf_obj.checksum

        # Case 1 set output
        func_expr.output = "out1"
        binder = StatementBinder(StatementBinderContext(mock_catalog))
        binder._bind_func_expr(func_expr)

        mock_get_file_checksum.assert_called_with(udf_obj.impl_file_path)
        mock_get_name.assert_called_with(func_expr.name)
        mock_get_udf_outputs.assert_called_with(udf_obj)
        mock_load_udf_class_from_file.assert_called_with(
            udf_obj.impl_file_path, udf_obj.name
        )
        self.assertEqual(func_expr.output_objs, [obj1])
        print(str(func_expr.alias))
        self.assertEqual(
            func_expr.alias,
            Alias("func_expr", ["out1"]),
        )
        self.assertEqual(func_expr.function(), "load_udf_class_from_file")

        # Case 2 output not set
        func_expr.output = None
        func_expr.alias = Alias("func_expr")
        binder = StatementBinder(StatementBinderContext(mock_catalog))
        binder._bind_func_expr(func_expr)

        mock_get_file_checksum.assert_called_with(udf_obj.impl_file_path)
        mock_get_name.assert_called_with(func_expr.name)
        mock_get_udf_outputs.assert_called_with(udf_obj)
        mock_load_udf_class_from_file.assert_called_with(
            udf_obj.impl_file_path, udf_obj.name
        )
        self.assertEqual(func_expr.output_objs, func_output_objs)
        self.assertEqual(
            func_expr.alias,
            Alias(
                "func_expr",
                ["out1", "out2"],
            ),
        )
        self.assertEqual(func_expr.function(), "load_udf_class_from_file")

        # Raise error if the class object cannot be created
        mock_load_udf_class_from_file.reset_mock()
        mock_error_msg = "mock_load_udf_class_from_file_error"
        mock_load_udf_class_from_file.side_effect = MagicMock(
            side_effect=RuntimeError(mock_error_msg)
        )
        binder = StatementBinder(StatementBinderContext(mock_catalog))
        with self.assertRaises(BinderError) as cm:
            binder._bind_func_expr(func_expr)
        err_msg = (
            f"{mock_error_msg}. Please verify that the UDF class name in the"
            "implementation file matches the UDF name."
        )
        self.assertEqual(str(cm.exception), err_msg)

    @patch("evadb.binder.statement_binder.check_table_object_is_groupable")
    @patch("evadb.binder.statement_binder.check_groupby_pattern")
    def test_bind_select_statement(self, is_groupable_mock, groupby_mock):
        with patch.object(StatementBinder, "bind") as mock_binder:
            binder = StatementBinder(StatementBinderContext(MagicMock()))
            select_statement = MagicMock()
            mocks = [MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()]
            select_statement.target_list = mocks[:2]
            select_statement.orderby_list = [(mocks[2], 0), (mocks[3], 0)]
            select_statement.groupby_clause = mocks[4]
            select_statement.groupby_clause.value = "8 frames"
            binder._bind_select_statement(select_statement)
            mock_binder.assert_any_call(select_statement.from_table)
            mock_binder.assert_any_call(select_statement.where_clause)
            mock_binder.assert_any_call(select_statement.groupby_clause)
            mock_binder.assert_any_call(select_statement.union_link)
            is_groupable_mock.assert_called()
            for mock in mocks:
                mock_binder.assert_any_call(mock)

    @patch("evadb.binder.statement_binder.StatementBinderContext")
    def test_bind_select_statement_union_starts_new_context(self, mock_ctx):
        with patch.object(StatementBinder, "bind"):
            binder = StatementBinder(StatementBinderContext(MagicMock()))
            select_statement = MagicMock()
            select_statement.union_link = None
            select_statement.groupby_clause = None
            binder._bind_select_statement(select_statement)
            self.assertEqual(mock_ctx.call_count, 0)

            binder = StatementBinder(StatementBinderContext(MagicMock()))
            select_statement = MagicMock()
            select_statement.groupby_clause = None
            binder._bind_select_statement(select_statement)
            self.assertEqual(mock_ctx.call_count, 1)

    def test_bind_unknown_object(self):
        class UnknownType:
            pass

        with self.assertRaises(NotImplementedError):
            binder = StatementBinder(StatementBinderContext(MagicMock()))
            binder.bind(UnknownType())

    def test_bind_create_index(self):
        with patch.object(StatementBinder, "bind"):
            catalog = MagicMock()
            binder = StatementBinder(StatementBinderContext(catalog))
            create_index_statement = MagicMock()

            with self.assertRaises(AssertionError):
                binder._bind_create_index_statement(create_index_statement)

            create_index_statement.col_list = ["foo"]
            udf_obj = MagicMock()
            output = MagicMock()
            udf_obj.outputs = [output]

            with patch.object(
                catalog(), "get_udf_catalog_entry_by_name", return_value=udf_obj
            ):
                with self.assertRaises(AssertionError):
                    binder._bind_create_index_statement(create_index_statement)
                output.array_type = NdArrayType.FLOAT32
                with self.assertRaises(AssertionError):
                    binder._bind_create_index_statement(create_index_statement)
                output.array_dimensions = [1, 100]
                binder._bind_create_index_statement(create_index_statement)

            create_index_statement.udf_func = None
            col_def = MagicMock()
            col_def.name = "a"
            create_index_statement.col_list = [col_def]
            col = MagicMock()
            col.name = "a"
            create_index_statement.table_ref.table.table_obj.columns = [col]

            with self.assertRaises(AssertionError):
                binder._bind_create_index_statement(create_index_statement)
            col.array_type = NdArrayType.FLOAT32
            with self.assertRaises(AssertionError):
                binder._bind_create_index_statement(create_index_statement)
            col.array_dimensions = [1, 10]
            binder._bind_create_index_statement(create_index_statement)
