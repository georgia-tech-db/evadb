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
from inspect import isabstract, signature
from test.util import get_all_subclasses, get_mock_object

import pytest

from evadb.catalog.catalog_type import ColumnType
from evadb.catalog.models.column_catalog import ColumnCatalogEntry
from evadb.parser.table_ref import TableInfo, TableRef
from evadb.parser.types import FileFormatType, ObjectType
from evadb.plan_nodes.abstract_plan import AbstractPlan
from evadb.plan_nodes.create_function_plan import CreateFunctionPlan
from evadb.plan_nodes.create_plan import CreatePlan
from evadb.plan_nodes.drop_object_plan import DropObjectPlan
from evadb.plan_nodes.insert_plan import InsertPlan
from evadb.plan_nodes.load_data_plan import LoadDataPlan
from evadb.plan_nodes.rename_plan import RenamePlan
from evadb.plan_nodes.types import PlanOprType
from evadb.plan_nodes.union_plan import UnionPlan


@pytest.mark.notparallel
class PlanNodeTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_create_plan(self):
        dummy_info = TableInfo("dummy")

        columns = [
            ColumnCatalogEntry("id", ColumnType.INTEGER),
            ColumnCatalogEntry("name", ColumnType.TEXT, array_dimensions=[50]),
        ]
        dummy_plan_node = CreatePlan(dummy_info, columns, False)
        self.assertEqual(dummy_plan_node.opr_type, PlanOprType.CREATE)
        self.assertEqual(dummy_plan_node.if_not_exists, False)
        self.assertEqual(dummy_plan_node.table_info.table_name, "dummy")
        self.assertEqual(dummy_plan_node.column_list[0].name, "id")
        self.assertEqual(dummy_plan_node.column_list[1].name, "name")

    def test_rename_plan(self):
        dummy_info = TableInfo("old")
        dummy_old = TableRef(dummy_info)
        dummy_new = TableInfo("new")

        dummy_plan_node = RenamePlan(dummy_old, dummy_new)
        self.assertEqual(dummy_plan_node.opr_type, PlanOprType.RENAME)
        self.assertEqual(dummy_plan_node.old_table.table.table_name, "old")
        self.assertEqual(dummy_plan_node.new_name.table_name, "new")

    def test_insert_plan(self):
        video_id = 0
        column_ids = [0, 1]
        expression = type("AbstractExpression", (), {"evaluate": lambda: 1})
        values = [expression, expression]
        dummy_plan_node = InsertPlan(video_id, column_ids, values)
        self.assertEqual(dummy_plan_node.opr_type, PlanOprType.INSERT)

    def test_create_function_plan(self):
        function_name = "function"
        or_replace = False
        if_not_exists = True
        functionIO = "functionIO"
        inputs = [functionIO, functionIO]
        outputs = [functionIO]
        impl_path = "test"
        ty = "classification"
        node = CreateFunctionPlan(
            function_name, or_replace, if_not_exists, inputs, outputs, impl_path, ty
        )
        self.assertEqual(node.opr_type, PlanOprType.CREATE_FUNCTION)
        self.assertEqual(node.or_replace, or_replace)
        self.assertEqual(node.if_not_exists, if_not_exists)
        self.assertEqual(node.inputs, [functionIO, functionIO])
        self.assertEqual(node.outputs, [functionIO])
        self.assertEqual(node.impl_path, impl_path)
        self.assertEqual(node.function_type, ty)

    def test_drop_object_plan(self):
        object_type = ObjectType.TABLE
        function_name = "function"
        if_exists = True
        node = DropObjectPlan(object_type, function_name, if_exists)
        self.assertEqual(node.opr_type, PlanOprType.DROP_OBJECT)
        self.assertEqual(node.if_exists, True)
        self.assertEqual(node.object_type, ObjectType.TABLE)

    def test_load_data_plan(self):
        table_info = "info"
        file_path = "test.mp4"
        file_format = FileFormatType.VIDEO
        file_options = {}
        file_options["file_format"] = file_format
        column_list = None
        batch_mem_size = 3000
        plan_str = "LoadDataPlan(table_id={}, file_path={}, \
            column_list={}, \
            file_options={}, \
            batch_mem_size={})".format(
            table_info, file_path, column_list, file_options, batch_mem_size
        )
        plan = LoadDataPlan(
            table_info, file_path, column_list, file_options, batch_mem_size
        )
        self.assertEqual(plan.opr_type, PlanOprType.LOAD_DATA)
        self.assertEqual(plan.table_info, table_info)
        self.assertEqual(plan.file_path, file_path)
        self.assertEqual(plan.batch_mem_size, batch_mem_size)

        self.assertEqual(str(plan), plan_str)

    def test_union_plan(self):
        all = True
        plan = UnionPlan(all)
        self.assertEqual(plan.opr_type, PlanOprType.UNION)
        self.assertEqual(plan.all, all)

    def test_abstract_plan_str(self):
        derived_plan_classes = list(get_all_subclasses(AbstractPlan))
        for derived_plan_class in derived_plan_classes:
            sig = signature(derived_plan_class.__init__)
            params = sig.parameters
            plan_dict = {}
            if isabstract(derived_plan_class) is False:
                obj = get_mock_object(derived_plan_class, len(params))
                plan_dict[obj] = obj
