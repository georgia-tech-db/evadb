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
from unittest.mock import MagicMock, Mock, patch

from evadb.binder.binder_utils import BinderError
from evadb.binder.statement_binder import StatementBinder
from evadb.binder.statement_binder_context import StatementBinderContext
from evadb.catalog.catalog_type import ColumnType, NdArrayType
from evadb.catalog.models.utils import ColumnCatalogEntry
from evadb.catalog.sql_config import IDENTIFIER_COLUMN
from evadb.expression.tuple_value_expression import TupleValueExpression
from evadb.parser.alias import Alias
from evadb.parser.create_statement import ColumnDefinition


def assert_not_called_with(self, *args, **kwargs):
    try:
        self.assert_called_with(*args, **kwargs)
    except AssertionError:
        return
    raise AssertionError(
        "Expected %s to not have been called."
        % self._format_mock_call_signature(args, kwargs)
    )


Mock.assert_not_called_with = assert_not_called_with


class StatementBinderTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_bind_tuple_value_expression(self):
        with patch.object(StatementBinderContext, "get_binded_column") as mock:
            mock.return_value = ["table_alias", "col_obj"]
            binder = StatementBinder(StatementBinderContext(MagicMock()))
            tve = MagicMock()
            tve.name = "col_name"
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
                tableref.alias.alias_name,
                tableref.table.database_name,
                tableref.table.table_name,
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

    def test_bind_create_table_from_select_statement(self):
        with patch.object(StatementBinder, "bind") as mock_binder:
            binder = StatementBinder(StatementBinderContext(MagicMock()))

            output_obj = MagicMock()
            output_obj.type = ColumnType.INTEGER
            output_obj.array_type = NdArrayType.UINT8
            output_obj.array_dimensions = (1, 1)

            create_statement = MagicMock()
            create_statement.column_list = []
            create_statement.query.target_list = [
                TupleValueExpression(name="id", col_object=output_obj),
                TupleValueExpression(name="label", col_object=output_obj),
            ]

            binder._bind_create_statement(create_statement)
            mock_binder.assert_called_with(create_statement.query)
            self.assertEqual(2, len(create_statement.column_list))

    def test_bind_explain_statement(self):
        with patch.object(StatementBinder, "bind") as mock_binder:
            binder = StatementBinder(StatementBinderContext(MagicMock()))
            stmt = MagicMock()
            binder._bind_explain_statement(stmt)
            mock_binder.assert_called_with(stmt.explainable_stmt)

    def test_bind_func_expr_with_star(self):
        func_expr = MagicMock(
            name="func_expr", alias=Alias("func_expr"), output_col_aliases=[]
        )
        func_expr.name.lower.return_value = "func_expr"
        func_expr.children = [TupleValueExpression(name="*")]

        binderContext = MagicMock()
        tvp1 = ("T", "col1")
        tvp2 = ("T", "col2")
        binderContext._catalog.return_value.get_function_catalog_entry_by_name.return_value = (
            None
        )
        binderContext._get_all_alias_and_col_name.return_value = [tvp1, tvp2]

        with patch.object(StatementBinder, "bind") as mock_binder:
            binder = StatementBinder(binderContext)
            with self.assertRaises(BinderError):
                binder._bind_func_expr(func_expr)
            call1, call2 = mock_binder.call_args_list
            self.assertEqual(
                call1.args[0], TupleValueExpression(name=tvp1[1], table_alias=tvp1[0])
            )
            self.assertEqual(
                call2.args[0], TupleValueExpression(name=tvp2[1], table_alias=tvp2[0])
            )

    @patch("evadb.binder.statement_binder.load_function_class_from_file")
    def test_bind_func_expr(self, mock_load_function_class_from_file):
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
        function_obj = MagicMock()

        mock_catalog = MagicMock()
        mock_get_name = mock_catalog().get_function_catalog_entry_by_name = MagicMock()
        mock_get_name.return_value = function_obj

        mock_get_function_outputs = (
            mock_catalog().get_function_io_catalog_output_entries
        ) = MagicMock()
        mock_get_function_outputs.return_value = func_output_objs
        mock_load_function_class_from_file.return_value.return_value = (
            "load_function_class_from_file"
        )
        # mock_get_file_checksum.return_value = function_obj.checksum

        # Case 1 set output
        func_expr.output = "out1"
        binder = StatementBinder(StatementBinderContext(mock_catalog))
        binder._bind_func_expr(func_expr)

        # mock_get_file_checksum.assert_called_with(function_obj.impl_file_path)
        mock_get_name.assert_called_with(func_expr.name)
        mock_get_function_outputs.assert_called_with(function_obj)
        mock_load_function_class_from_file.assert_called_with(
            function_obj.impl_file_path, function_obj.name
        )
        self.assertEqual(func_expr.output_objs, [obj1])
        self.assertEqual(
            func_expr.alias,
            Alias("func_expr", ["out1"]),
        )
        self.assertEqual(func_expr.function(), "load_function_class_from_file")

        # Case 2 output not set
        func_expr.output = None
        func_expr.alias = Alias("func_expr")
        binder = StatementBinder(StatementBinderContext(mock_catalog))
        binder._bind_func_expr(func_expr)

        # mock_get_file_checksum.assert_called_with(function_obj.impl_file_path)
        mock_get_name.assert_called_with(func_expr.name)
        mock_get_function_outputs.assert_called_with(function_obj)
        mock_load_function_class_from_file.assert_called_with(
            function_obj.impl_file_path, function_obj.name
        )
        self.assertEqual(func_expr.output_objs, func_output_objs)
        self.assertEqual(
            func_expr.alias,
            Alias(
                "func_expr",
                ["out1", "out2"],
            ),
        )
        self.assertEqual(func_expr.function(), "load_function_class_from_file")

        # Raise error if the class object cannot be created
        mock_load_function_class_from_file.reset_mock()
        mock_error_msg = "mock_load_function_class_from_file_error"
        mock_load_function_class_from_file.side_effect = MagicMock(
            side_effect=RuntimeError(mock_error_msg)
        )
        binder = StatementBinder(StatementBinderContext(mock_catalog))
        with self.assertRaises(BinderError) as cm:
            binder._bind_func_expr(func_expr)
        err_msg = (
            f"{mock_error_msg}. Please verify that the function class name in the "
            "implementation file matches the function name."
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
            select_statement.from_table.chunk_params = None
            binder._bind_select_statement(select_statement)
            mock_binder.assert_any_call(select_statement.from_table)
            mock_binder.assert_any_call(select_statement.where_clause)
            mock_binder.assert_any_call(select_statement.groupby_clause)
            mock_binder.assert_any_call(select_statement.union_link)
            is_groupable_mock.assert_called()
            for mock in mocks:
                mock_binder.assert_any_call(mock)

    def test_bind_select_statement_without_from(self):
        with patch.object(StatementBinder, "bind") as mock_binder:
            binder = StatementBinder(StatementBinderContext(MagicMock()))
            expr = MagicMock()
            from evadb.parser.select_statement import SelectStatement

            select_statement = SelectStatement(target_list=[expr])
            binder._bind_select_statement(select_statement)
            mock_binder.assert_not_called_with(select_statement.from_table)
            mock_binder.assert_any_call(expr)

    @patch("evadb.binder.statement_binder.StatementBinderContext")
    def test_bind_select_statement_union_starts_new_context(self, mock_ctx):
        with patch.object(StatementBinder, "bind"):
            binder = StatementBinder(StatementBinderContext(MagicMock()))
            select_statement = MagicMock()
            select_statement.union_link = None
            select_statement.groupby_clause = None
            select_statement.from_table.chunk_params = None
            binder._bind_select_statement(select_statement)
            self.assertEqual(mock_ctx.call_count, 0)

            binder = StatementBinder(StatementBinderContext(MagicMock()))
            select_statement = MagicMock()
            select_statement.from_table.chunk_params = None
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
            function_obj = MagicMock()
            output = MagicMock()
            function_obj.outputs = [output]

            with patch.object(
                catalog(),
                "get_function_catalog_entry_by_name",
                return_value=function_obj,
            ):
                with self.assertRaises(AssertionError):
                    binder._bind_create_index_statement(create_index_statement)
                output.array_type = NdArrayType.FLOAT32
                with self.assertRaises(AssertionError):
                    binder._bind_create_index_statement(create_index_statement)
                output.array_dimensions = [1, 100]
                binder._bind_create_index_statement(create_index_statement)

            create_index_statement.function = None
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

    def test_bind_create_function_should_raise_without_predict_for_ludwig(self):
        with patch.object(StatementBinder, "bind"):
            create_function_statement = MagicMock()
            create_function_statement.function_type = "ludwig"
            create_function_statement.query.target_list = []
            create_function_statement.metadata = []
            binder = StatementBinder(StatementBinderContext(MagicMock()))
            with self.assertRaises(AssertionError):
                binder._bind_create_function_statement(create_function_statement)

    def test_bind_create_function_should_drop_row_id_for_select_star(self):
        with patch.object(StatementBinder, "bind"):
            create_function_statement = MagicMock()
            create_function_statement.function_type = "ludwig"
            row_id_col_obj = ColumnCatalogEntry(
                name=IDENTIFIER_COLUMN,
                type=MagicMock(),
                array_type=MagicMock(),
                array_dimensions=MagicMock(),
            )
            input_col_obj = ColumnCatalogEntry(
                name="input_column",
                type=MagicMock(),
                array_type=MagicMock(),
                array_dimensions=MagicMock(),
            )
            output_col_obj = ColumnCatalogEntry(
                name="predict_column",
                type=MagicMock(),
                array_type=MagicMock(),
                array_dimensions=MagicMock(),
            )
            create_function_statement.query.target_list = [
                TupleValueExpression(
                    name=IDENTIFIER_COLUMN, table_alias="a", col_object=row_id_col_obj
                ),
                TupleValueExpression(
                    name="input_column", table_alias="a", col_object=input_col_obj
                ),
                TupleValueExpression(
                    name="predict_column", table_alias="a", col_object=output_col_obj
                ),
            ]
            create_function_statement.metadata = [("predict", "predict_column")]
            binder = StatementBinder(StatementBinderContext(MagicMock()))
            binder._bind_create_function_statement(create_function_statement)

            self.assertEqual(
                create_function_statement.query.target_list,
                [
                    TupleValueExpression(
                        name="input_column", table_alias="a", col_object=input_col_obj
                    ),
                    TupleValueExpression(
                        name="predict_column",
                        table_alias="a",
                        col_object=output_col_obj,
                    ),
                ],
            )

            expected_inputs = [
                ColumnDefinition(
                    "input_column",
                    input_col_obj.type,
                    input_col_obj.array_type,
                    input_col_obj.array_dimensions,
                )
            ]
            expected_outputs = [
                ColumnDefinition(
                    "predict_column_predictions",
                    output_col_obj.type,
                    output_col_obj.array_type,
                    output_col_obj.array_dimensions,
                )
            ]
            self.assertEqual(create_function_statement.inputs, expected_inputs)
            self.assertEqual(create_function_statement.outputs, expected_outputs)

    def test_bind_create_function_should_bind_forecast_with_default_columns(self):
        with patch.object(StatementBinder, "bind"):
            create_function_statement = MagicMock()
            create_function_statement.function_type = "forecasting"
            id_col_obj = ColumnCatalogEntry(
                name="unique_id",
                type=MagicMock(),
                array_type=MagicMock(),
                array_dimensions=MagicMock(),
            )
            ds_col_obj = ColumnCatalogEntry(
                name="ds",
                type=MagicMock(),
                array_type=MagicMock(),
                array_dimensions=MagicMock(),
            )
            y_col_obj = ColumnCatalogEntry(
                name="y",
                type=MagicMock(),
                array_type=MagicMock(),
                array_dimensions=MagicMock(),
            )
            create_function_statement.query.target_list = [
                TupleValueExpression(
                    name=id_col_obj.name, table_alias="a", col_object=id_col_obj
                ),
                TupleValueExpression(
                    name=ds_col_obj.name, table_alias="a", col_object=ds_col_obj
                ),
                TupleValueExpression(
                    name=y_col_obj.name, table_alias="a", col_object=y_col_obj
                ),
            ]
            create_function_statement.metadata = []
            binder = StatementBinder(StatementBinderContext(MagicMock()))
            binder._bind_create_function_statement(create_function_statement)

            expected_inputs = [
                ColumnDefinition(
                    "horizon",
                    ColumnType.INTEGER,
                    None,
                    None,
                )
            ]
            expected_outputs = list(
                [
                    ColumnDefinition(
                        col_obj.name,
                        col_obj.type,
                        col_obj.array_type,
                        col_obj.array_dimensions,
                    )
                    for col_obj in (id_col_obj, ds_col_obj, y_col_obj)
                ]
            )
            self.assertEqual(create_function_statement.inputs, expected_inputs)
            self.assertEqual(create_function_statement.outputs, expected_outputs)

    def test_bind_create_function_should_bind_forecast_with_renaming_columns(self):
        with patch.object(StatementBinder, "bind"):
            create_function_statement = MagicMock()
            create_function_statement.function_type = "forecasting"
            id_col_obj = ColumnCatalogEntry(
                name="type",
                type=MagicMock(),
                array_type=MagicMock(),
                array_dimensions=MagicMock(),
            )
            ds_col_obj = ColumnCatalogEntry(
                name="saledate",
                type=MagicMock(),
                array_type=MagicMock(),
                array_dimensions=MagicMock(),
            )
            y_col_obj = ColumnCatalogEntry(
                name="ma",
                type=MagicMock(),
                array_type=MagicMock(),
                array_dimensions=MagicMock(),
            )
            create_function_statement.query.target_list = [
                TupleValueExpression(
                    name=id_col_obj.name, table_alias="a", col_object=id_col_obj
                ),
                TupleValueExpression(
                    name=ds_col_obj.name, table_alias="a", col_object=ds_col_obj
                ),
                TupleValueExpression(
                    name=y_col_obj.name, table_alias="a", col_object=y_col_obj
                ),
            ]
            create_function_statement.metadata = [
                ("predict", "ma"),
                ("id", "type"),
                ("time", "saledate"),
            ]
            binder = StatementBinder(StatementBinderContext(MagicMock()))
            binder._bind_create_function_statement(create_function_statement)

            expected_inputs = [
                ColumnDefinition(
                    "horizon",
                    ColumnType.INTEGER,
                    None,
                    None,
                )
            ]
            expected_outputs = list(
                [
                    ColumnDefinition(
                        col_obj.name,
                        col_obj.type,
                        col_obj.array_type,
                        col_obj.array_dimensions,
                    )
                    for col_obj in (id_col_obj, ds_col_obj, y_col_obj)
                ]
            )
            self.assertEqual(create_function_statement.inputs, expected_inputs)
            self.assertEqual(create_function_statement.outputs, expected_outputs)

    def test_bind_create_function_should_raise_forecast_with_unexpected_columns(self):
        with patch.object(StatementBinder, "bind"):
            create_function_statement = MagicMock()
            create_function_statement.function_type = "forecasting"
            id_col_obj = ColumnCatalogEntry(
                name="type",
                type=MagicMock(),
                array_type=MagicMock(),
                array_dimensions=MagicMock(),
            )
            ds_col_obj = ColumnCatalogEntry(
                name="saledate",
                type=MagicMock(),
                array_type=MagicMock(),
                array_dimensions=MagicMock(),
            )
            y_col_obj = ColumnCatalogEntry(
                name="ma",
                type=MagicMock(),
                array_type=MagicMock(),
                array_dimensions=MagicMock(),
            )
            create_function_statement.query.target_list = [
                TupleValueExpression(
                    name=id_col_obj.name, table_alias="a", col_object=id_col_obj
                ),
                TupleValueExpression(
                    name=ds_col_obj.name, table_alias="a", col_object=ds_col_obj
                ),
                TupleValueExpression(
                    name=y_col_obj.name, table_alias="a", col_object=y_col_obj
                ),
            ]
            create_function_statement.metadata = [
                ("predict", "ma"),
                ("time", "saledate"),
            ]
            binder = StatementBinder(StatementBinderContext(MagicMock()))

            with self.assertRaises(BinderError) as cm:
                binder._bind_create_function_statement(create_function_statement)

            err_msg = "Unexpected column type found for forecasting function."
            self.assertEqual(str(cm.exception), err_msg)

    def test_bind_create_function_should_raise_forecast_missing_required_columns(self):
        with patch.object(StatementBinder, "bind"):
            create_function_statement = MagicMock()
            create_function_statement.function_type = "forecasting"
            id_col_obj = ColumnCatalogEntry(
                name="type",
                type=MagicMock(),
                array_type=MagicMock(),
                array_dimensions=MagicMock(),
            )
            ds_col_obj = ColumnCatalogEntry(
                name="saledate",
                type=MagicMock(),
                array_type=MagicMock(),
                array_dimensions=MagicMock(),
            )
            create_function_statement.query.target_list = [
                TupleValueExpression(
                    name=id_col_obj.name, table_alias="a", col_object=id_col_obj
                ),
                TupleValueExpression(
                    name=ds_col_obj.name, table_alias="a", col_object=ds_col_obj
                ),
            ]
            create_function_statement.metadata = [
                ("id", "type"),
                ("time", "saledate"),
                ("predict", "ma"),
            ]
            binder = StatementBinder(StatementBinderContext(MagicMock()))

            with self.assertRaises(AssertionError) as cm:
                binder._bind_create_function_statement(create_function_statement)

            err_msg = "Missing required {'ma'} columns for forecasting function."
            self.assertEqual(str(cm.exception), err_msg)
