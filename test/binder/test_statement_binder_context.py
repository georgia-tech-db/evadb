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
from unittest.mock import MagicMock, patch

from eva.binder.binder_utils import BinderError
from eva.binder.statement_binder_context import StatementBinderContext
from eva.expression.function_expression import FunctionExpression
from eva.expression.tuple_value_expression import TupleValueExpression


class StatementBinderTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_check_duplicate_alias(self):
        with self.assertRaises(BinderError):
            ctx = StatementBinderContext()
            ctx._derived_table_alias_map["alias"] = MagicMock()
            ctx._check_duplicate_alias("alias")

        with self.assertRaises(BinderError):
            ctx = StatementBinderContext()
            ctx._table_alias_map["alias"] = MagicMock()
            ctx._check_duplicate_alias("alias")

        # no duplicate
        ctx = StatementBinderContext()
        ctx._check_duplicate_alias("alias")

    @patch("eva.binder.statement_binder_context.CatalogManager")
    def test_add_table_alias(self, mock_catalog):
        mock_get = mock_catalog().get_table_catalog_entry = MagicMock()
        mock_get.return_value = "table_obj"
        ctx = StatementBinderContext()

        mock_check = ctx._check_duplicate_alias = MagicMock()
        ctx.add_table_alias("alias", "table_name")
        mock_check.assert_called_with("alias")
        mock_get.assert_called_with("table_name")
        self.assertEqual(ctx._table_alias_map["alias"], "table_obj")

    def test_add_derived_table_alias(self):
        objs = [MagicMock(), MagicMock()]
        exprs = [
            MagicMock(spec=TupleValueExpression, col_name="A", col_object="A_obj"),
            MagicMock(spec=FunctionExpression, output_objs=objs),
        ]
        ctx = StatementBinderContext()

        mock_check = ctx._check_duplicate_alias = MagicMock()
        ctx.add_derived_table_alias("alias", exprs)

        mock_check.assert_called_with("alias")
        col_map = {"A": "A_obj", objs[0].name: objs[0], objs[1].name: objs[1]}
        self.assertEqual(ctx._derived_table_alias_map["alias"], col_map)

    def test_get_binded_column_should_search_all(self):
        ctx = StatementBinderContext()
        mock_search_all = ctx._search_all_alias_maps = MagicMock()
        mock_search_all.return_value = ("alias", "col_obj")

        result = ctx.get_binded_column("col_name")
        mock_search_all.assert_called_once_with("col_name")
        self.assertEqual(result, ("alias", "col_obj"))

    def test_get_binded_column_check_table_alias_map(self):
        ctx = StatementBinderContext()
        mock_table_map = ctx._check_table_alias_map = MagicMock()
        mock_table_map.return_value = "col_obj"
        result = ctx.get_binded_column("col_name", "alias")
        mock_table_map.assert_called_once_with("alias", "col_name")
        self.assertEqual(result, ("alias", "col_obj"))

    def test_get_binded_column_check_derived_table_alias_map(self):
        ctx = StatementBinderContext()
        mock_table_map = ctx._check_table_alias_map = MagicMock()
        mock_table_map.return_value = None
        mock_derived_map = ctx._check_derived_table_alias_map = MagicMock()
        mock_derived_map.return_value = "col_obj"

        result = ctx.get_binded_column("col_name", "alias")
        mock_table_map.assert_called_once_with("alias", "col_name")
        mock_derived_map.assert_called_once_with("alias", "col_name")
        self.assertEqual(result, ("alias", "col_obj"))

    def test_get_binded_column_raise_error(self):
        # no alias
        with self.assertRaises(BinderError):
            ctx = StatementBinderContext()
            mock_search_all = ctx._search_all_alias_maps = MagicMock()
            mock_search_all.return_value = (None, None)
            ctx.get_binded_column("col_name")
        # with alias
        with self.assertRaises(BinderError):
            ctx = StatementBinderContext()
            mock_table_map = ctx._check_table_alias_map = MagicMock()
            mock_table_map.return_value = None
            mock_derived_map = ctx._check_derived_table_alias_map = MagicMock()
            mock_derived_map.return_value = None
            ctx.get_binded_column("col_name", "alias")

    @patch("eva.binder.statement_binder_context.CatalogManager")
    def test_check_table_alias_map(self, mock_catalog):
        mock_get_column_object = mock_catalog().get_column_catalog_entry = MagicMock()
        mock_get_column_object.return_value = "catalog_value"
        # key exists
        ctx = StatementBinderContext()
        ctx._table_alias_map["alias"] = "table_obj"
        result = ctx._check_table_alias_map("alias", "col_name")
        mock_get_column_object.assert_called_once_with("table_obj", "col_name")
        self.assertEqual(result, "catalog_value")

        # key does not exixt
        mock_get_column_object.reset_mock()
        ctx = StatementBinderContext()
        result = ctx._check_table_alias_map("alias", "col_name")
        mock_get_column_object.assert_not_called()
        self.assertEqual(result, None)

    def test_check_derived_table_alias_map(self):
        # key exists
        ctx = StatementBinderContext()
        obj1 = MagicMock()
        obj2 = MagicMock()
        col_map = {"col1": obj1, "col2": obj2}
        ctx._derived_table_alias_map["alias"] = col_map
        result = ctx._check_derived_table_alias_map("alias", "col1")
        self.assertEqual(result, obj1)
        result = ctx._check_derived_table_alias_map("alias", "col2")
        self.assertEqual(result, obj2)
        # key does not exixt
        ctx = StatementBinderContext()
        result = ctx._check_derived_table_alias_map("alias", "col3")
        self.assertEqual(result, None)

    def test_search_all_alias_maps(self):
        ctx = StatementBinderContext()
        check_table_map = ctx._check_table_alias_map = MagicMock()
        check_derived_map = ctx._check_derived_table_alias_map = MagicMock()

        # only _table_alias_map has entry
        check_table_map.return_value = "col_obj"
        ctx._table_alias_map["alias"] = "col_name"
        ctx._derived_table_alias_map = {}
        result = ctx._search_all_alias_maps("col_name")
        check_table_map.assert_called_once_with("alias", "col_name")
        check_derived_map.assert_not_called()
        self.assertEqual(result, ("alias", "col_obj"))

        # only _derived_table_alias_map
        check_derived_map.return_value = "derived_col_obj"
        ctx._table_alias_map = {}
        ctx._derived_table_alias_map["alias"] = "col_name"
        result = ctx._search_all_alias_maps("col_name")
        check_table_map.assert_called_once_with("alias", "col_name")
        check_table_map.assert_called_once_with("alias", "col_name")
        self.assertEqual(result, ("alias", "derived_col_obj"))

    def test_search_all_alias_raise_duplicate_error(self):
        with self.assertRaises(BinderError):
            ctx = StatementBinderContext()
            ctx._check_table_alias_map = MagicMock()
            ctx._check_derived_table_alias_map = MagicMock()
            # duplicate
            ctx._table_alias_map["alias"] = "col_name"
            ctx._derived_table_alias_map["alias"] = "col_name"
            ctx._search_all_alias_maps("col_name")
