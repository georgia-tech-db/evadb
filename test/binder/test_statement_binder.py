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
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from eva.binder.binder_utils import BinderError
from eva.binder.statement_binder import StatementBinder
from eva.binder.statement_binder_context import StatementBinderContext
from eva.catalog.catalog_manager import CatalogManager
from eva.parser.alias import Alias
from eva.parser.types import FileFormatType


class StatementBinderTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_bind_tuple_value_expression(self):
        with patch.object(StatementBinderContext, "get_binded_column") as mock:
            mock.return_value = ["table_alias", "col_obj"]
            binder = StatementBinder(StatementBinderContext())
            tve = MagicMock()
            tve.col_name = "col_name"
            binder._bind_tuple_expr(tve)
            col_alias = "{}.{}".format("table_alias", "col_name")
            mock.assert_called_with(tve.col_name, tve.table_alias)
            self.assertEqual(tve.col_object, "col_obj")
            self.assertEqual(tve.col_alias, col_alias)

    @patch("eva.binder.statement_binder.bind_table_info")
    def test_bind_tableref(self, mock_bind_tabe_info):
        with patch.object(StatementBinderContext, "add_table_alias") as mock:
            binder = StatementBinder(StatementBinderContext())
            tableref = MagicMock()
            tableref.is_table_atom.return_value = True
            binder._bind_tableref(tableref)
            mock.assert_called_with(
                tableref.alias.alias_name, tableref.table.table_name
            )
            mock_bind_tabe_info.assert_called_once_with(tableref.table)

        with patch.object(StatementBinder, "bind") as mock_binder:
            with patch.object(
                StatementBinderContext, "add_derived_table_alias"
            ) as mock_context:
                binder = StatementBinder(StatementBinderContext())
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
            binder = StatementBinder(StatementBinderContext())
            tableref = MagicMock()
            tableref.is_table_atom.return_value = False
            tableref.is_select.return_value = False
            tableref.is_join.return_value = False
            binder._bind_tableref(tableref)
            mock_binder.assert_called_with(tableref.table_valued_expr.func_expr)

    def test_bind_tableref_with_join(self):
        with patch.object(StatementBinder, "bind") as mock_binder:
            binder = StatementBinder(StatementBinderContext())
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
                binder = StatementBinder(StatementBinderContext())
                tableref = MagicMock()
                tableref.is_select.return_value = False
                tableref.is_table_valued_expr.return_value = False
                tableref.is_join.return_value = False
                tableref.is_table_atom.return_value = False
                binder._bind_tableref(tableref)

    @patch("eva.binder.statement_binder.StatementBinderContext")
    def test_bind_tableref_starts_new_context(self, mock_ctx):
        with patch.object(StatementBinder, "bind"):
            binder = StatementBinder(StatementBinderContext())
            tableref = MagicMock()
            tableref.is_table_atom.return_value = False
            tableref.is_join.return_value = False
            tableref.is_select.return_value = True
            binder._bind_tableref(tableref)
            self.assertEqual(mock_ctx.call_count, 1)

    def test_bind_create_mat_statement(self):
        with patch.object(StatementBinder, "bind") as mock_binder:
            binder = StatementBinder(StatementBinderContext())
            mat_statement = MagicMock()
            binder._bind_create_mat_statement(mat_statement)
            mock_binder.assert_called_with(mat_statement.query)

    def test_bind_explain_statement(self):
        with patch.object(StatementBinder, "bind") as mock_binder:
            binder = StatementBinder(StatementBinderContext())
            stmt = MagicMock()
            binder._bind_explain_statement(stmt)
            mock_binder.assert_called_with(stmt.explainable_stmt)

    @patch("eva.binder.statement_binder.CatalogManager")
    @patch("eva.binder.statement_binder.path_to_class")
    def test_bind_func_expr(self, mock_path_to_class, mock_catalog):
        # setup
        func_expr = MagicMock(
            name="func_expr", alias=Alias("func_expr"), output_col_aliases=[]
        )
        func_expr.name.lower.return_value = "func_expr"
        obj1 = MagicMock()
        obj1.name.lower.return_value = "out1"
        obj2 = MagicMock()
        obj2.name.lower.return_value = "out2"
        func_ouput_objs = [obj1, obj2]
        udf_obj = MagicMock()
        mock_get_name = mock_catalog().get_udf_by_name = MagicMock()
        mock_get_name.return_value = udf_obj

        mock_get_udf_outputs = mock_catalog().get_udf_outputs = MagicMock()
        mock_get_udf_outputs.return_value = func_ouput_objs
        mock_path_to_class.return_value.return_value = "path_to_class"

        # Case 1 set output
        func_expr.output = "out1"
        binder = StatementBinder(StatementBinderContext())
        binder._bind_func_expr(func_expr)

        mock_get_name.assert_called_with(func_expr.name)
        mock_get_udf_outputs.assert_called_with(udf_obj)
        mock_path_to_class.assert_called_with(udf_obj.impl_file_path, udf_obj.name)
        self.assertEqual(func_expr.output_objs, [obj1])
        print(str(func_expr.alias))
        self.assertEqual(
            func_expr.alias,
            Alias("func_expr", ["out1"]),
        )
        self.assertEqual(func_expr.function(), "path_to_class")

        # Case 2 output not set
        func_expr.output = None
        func_expr.alias = Alias("func_expr")
        binder = StatementBinder(StatementBinderContext())
        binder._bind_func_expr(func_expr)

        mock_get_name.assert_called_with(func_expr.name)
        mock_get_udf_outputs.assert_called_with(udf_obj)
        mock_path_to_class.assert_called_with(udf_obj.impl_file_path, udf_obj.name)
        self.assertEqual(func_expr.output_objs, func_ouput_objs)
        self.assertEqual(
            func_expr.alias,
            Alias(
                "func_expr",
                ["out1", "out2"],
            ),
        )
        self.assertEqual(func_expr.function(), "path_to_class")

        # Raise error if the class object cannot be created
        mock_path_to_class.reset_mock()
        mock_error_msg = "mock_path_to_class_error"
        mock_path_to_class.side_effect = MagicMock(
            side_effect=RuntimeError(mock_error_msg)
        )
        binder = StatementBinder(StatementBinderContext())
        with self.assertRaises(BinderError) as cm:
            binder._bind_func_expr(func_expr)
        err_msg = (
            f"{mock_error_msg}. Please verify that the UDF class name in the"
            "implementation file matches the UDF name."
        )
        self.assertEqual(str(cm.exception), err_msg)

    def test_bind_select_statement(self):
        with patch.object(StatementBinder, "bind") as mock_binder:
            binder = StatementBinder(StatementBinderContext())
            select_statement = MagicMock()
            mocks = [MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()]
            select_statement.target_list = mocks[:2]
            select_statement.orderby_list = [(mocks[2], 0), (mocks[3], 0)]
            select_statement.groupby_clause = mocks[4]
            select_statement.groupby_clause.value = "8f"
            binder._bind_select_statement(select_statement)
            mock_binder.assert_any_call(select_statement.from_table)
            mock_binder.assert_any_call(select_statement.where_clause)
            mock_binder.assert_any_call(select_statement.groupby_clause)
            mock_binder.assert_any_call(select_statement.union_link)
            for mock in mocks:
                mock_binder.assert_any_call(mock)

    @patch("eva.binder.statement_binder.StatementBinderContext")
    def test_bind_select_statement_union_starts_new_context(self, mock_ctx):
        with patch.object(StatementBinder, "bind"):
            binder = StatementBinder(StatementBinderContext())
            select_statement = MagicMock()
            select_statement.union_link = None
            select_statement.groupby_clause = None
            binder._bind_select_statement(select_statement)
            self.assertEqual(mock_ctx.call_count, 0)

            binder = StatementBinder(StatementBinderContext())
            select_statement = MagicMock()
            select_statement.groupby_clause = None
            binder._bind_select_statement(select_statement)
            self.assertEqual(mock_ctx.call_count, 1)

    @patch("eva.binder.statement_binder.create_video_metadata")
    @patch("eva.binder.statement_binder.TupleValueExpression")
    def test_bind_load_video_statement(self, mock_tve, mock_create):
        load_statement = MagicMock()
        load_statement.file_options = {"file_format": FileFormatType.VIDEO}
        load_statement.column_list = None
        load_statement.path = "video_path"
        column = MagicMock()
        table_ref_obj = MagicMock()
        table_ref_obj.columns = [column]
        table_ref_obj.name = "table_alias"
        load_statement.table_ref.table.table_obj = table_ref_obj
        load_statement.table_ref.table.table_name = "table_name"
        mock_tve.return_value = tve_return_value = MagicMock()

        with patch.object(StatementBinder, "bind") as mock_binder:
            with patch.object(Path, "exists") as mock_exists:
                mock_exists.return_value = True
                binder = StatementBinder(StatementBinderContext())
                binder._bind_load_and_upload_data_statement(load_statement)
                mock_binder.assert_any_call(load_statement.table_ref)
                mock_create.assert_any_call("table_name")
                mock_tve.assert_called_with(
                    col_name=column.name,
                    table_alias="table_alias",
                    col_object=column,
                )
                mock_binder.assert_any_call(tve_return_value)
                self.assertEqual(load_statement.column_list, [tve_return_value])

    @patch("eva.binder.statement_binder.create_video_metadata")
    @patch("eva.binder.statement_binder.TupleValueExpression")
    def test_bind_load_data_raises(self, mock_tve, mock_create):
        load_statement = MagicMock()
        column = MagicMock()
        file_path = "file_path"
        load_statement.column_list = [column]
        load_statement.table_ref.table.table_obj = None
        with self.assertRaises(BinderError):
            with patch.object(StatementBinder, "bind"):
                binder = StatementBinder(StatementBinderContext())
                binder._bind_load_and_upload_data_statement(load_statement)

        # test should raise if the file path does not exists
        load_statement.file_options = {"file_format": FileFormatType.VIDEO}
        load_statement.path = file_path
        with patch.object(StatementBinder, "bind"):
            with patch.object(
                CatalogManager, "check_table_exists"
            ) as mock_catalog_check:
                mock_catalog_check.return_value = False
                with patch.object(Path, "exists") as mock_exists:
                    mock_exists.return_value = False
                    with self.assertRaises(BinderError) as cm:
                        binder = StatementBinder(StatementBinderContext())
                        binder._bind_load_and_upload_data_statement(load_statement)
                    self.assertEqual(
                        str(cm.exception), f"Video file {file_path} does not exist."
                    )

    def test_bind_unknown_object(self):
        class UnknownType:
            pass

        with self.assertRaises(NotImplementedError):
            binder = StatementBinder(StatementBinderContext())
            binder.bind(UnknownType())

    @patch("eva.binder.statement_binder.sys")
    def test_bind_with_python37(self, mock_sys):
        mock_sys.version_info = (3, 8)
        with patch.object(StatementBinderContext, "get_binded_column") as mock:
            mock.return_value = ["table_alias", "col_obj"]
            binder = StatementBinder(StatementBinderContext())
            tve = MagicMock()
            tve.col_name = "col_name"
            binder._bind_tuple_expr(tve)
            col_alias = "{}.{}".format("table_alias", "col_name")
            mock.assert_called_with(tve.col_name, tve.table_alias)
            self.assertEqual(tve.col_object, "col_obj")
            self.assertEqual(tve.col_alias, col_alias)
