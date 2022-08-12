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

from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.column_type import ColumnType
from eva.catalog.models.df_column import DataFrameColumn
from eva.parser.table_ref import TableInfo, TableRef
from eva.parser.types import FileFormatType
from eva.planner.create_mat_view_plan import CreateMaterializedViewPlan
from eva.planner.create_plan import CreatePlan
from eva.planner.create_udf_plan import CreateUDFPlan
from eva.planner.drop_plan import DropPlan
from eva.planner.drop_udf_plan import DropUDFPlan
from eva.planner.insert_plan import InsertPlan
from eva.planner.load_data_plan import LoadDataPlan
from eva.planner.rename_plan import RenamePlan
from eva.planner.types import PlanOprType
from eva.planner.union_plan import UnionPlan
from eva.planner.upload_plan import UploadPlan


class PlanNodeTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_create_plan(self):
        dummy_info = TableInfo("dummy")
        dummy_table = TableRef(dummy_info)

        CatalogManager().reset()
        columns = [
            DataFrameColumn("id", ColumnType.INTEGER),
            DataFrameColumn("name", ColumnType.TEXT, array_dimensions=[50]),
        ]
        dummy_plan_node = CreatePlan(dummy_table, columns, False)
        self.assertEqual(dummy_plan_node.opr_type, PlanOprType.CREATE)
        self.assertEqual(dummy_plan_node.if_not_exists, False)
        self.assertEqual(dummy_plan_node.table_ref.table.table_name, "dummy")
        self.assertEqual(dummy_plan_node.column_list[0].name, "id")
        self.assertEqual(dummy_plan_node.column_list[1].name, "name")

    def test_rename_plan(self):
        dummy_info = TableInfo("old")
        dummy_old = TableRef(dummy_info)
        dummy_new = TableInfo("new")

        CatalogManager().reset()
        dummy_plan_node = RenamePlan(dummy_old, dummy_new)
        self.assertEqual(dummy_plan_node.opr_type, PlanOprType.RENAME)
        self.assertEqual(dummy_plan_node.old_table.table.table_name, "old")
        self.assertEqual(dummy_plan_node.new_name.table_name, "new")

    def test_drop_plan(self):
        dummy_info = TableInfo("dummy")
        dummy_table = TableRef(dummy_info)

        CatalogManager().reset()
        dummy_plan_node = DropPlan([dummy_table], False)

        self.assertEqual(dummy_plan_node.opr_type, PlanOprType.DROP)
        self.assertEqual(dummy_plan_node.table_refs[0].table.table_name, "dummy")

    def test_insert_plan(self):
        video_id = 0
        column_ids = [0, 1]
        expression = type("AbstractExpression", (), {"evaluate": lambda: 1})
        values = [expression, expression]
        dummy_plan_node = InsertPlan(video_id, column_ids, values)
        self.assertEqual(dummy_plan_node.opr_type, PlanOprType.INSERT)

    def test_create_udf_plan(self):
        udf_name = "udf"
        if_not_exists = True
        udfIO = "udfIO"
        inputs = [udfIO, udfIO]
        outputs = [udfIO]
        impl_path = "test"
        ty = "classification"
        node = CreateUDFPlan(udf_name, if_not_exists, inputs, outputs, impl_path, ty)
        self.assertEqual(node.opr_type, PlanOprType.CREATE_UDF)
        self.assertEqual(node.if_not_exists, True)
        self.assertEqual(node.inputs, [udfIO, udfIO])
        self.assertEqual(node.outputs, [udfIO])
        self.assertEqual(node.impl_path, impl_path)
        self.assertEqual(node.udf_type, ty)

    def test_drop_udf_plan(self):
        udf_name = "udf"
        if_exists = True
        node = DropUDFPlan(udf_name, if_exists)
        self.assertEqual(node.opr_type, PlanOprType.DROP_UDF)
        self.assertEqual(node.if_exists, True)

    def test_load_data_plan(self):
        table_metainfo = "meta_info"
        file_path = "test.mp4"
        file_format = FileFormatType.VIDEO
        file_options = {}
        file_options["file_format"] = file_format
        column_list = None
        batch_mem_size = 3000
        plan_str = "LoadDataPlan(table_id={}, file_path={}, \
            batch_mem_size={}, \
            column_list={}, \
            file_options={})".format(
            table_metainfo, file_path, batch_mem_size, column_list, file_options
        )
        plan = LoadDataPlan(
            table_metainfo, file_path, batch_mem_size, column_list, file_options
        )
        self.assertEqual(plan.opr_type, PlanOprType.LOAD_DATA)
        self.assertEqual(plan.table_metainfo, table_metainfo)
        self.assertEqual(plan.file_path, file_path)
        self.assertEqual(plan.batch_mem_size, batch_mem_size)

        print(f"plan: {str(plan)}")
        print(f"plan_str: {plan_str}")

        self.assertEqual(str(plan), plan_str)

    def test_upload_plan(self):
        file_path = "test.mp4"
        video_blob = "b'AAAA'"
        table_metainfo = "meta_info"
        file_format = FileFormatType.VIDEO
        file_options = {}
        file_options["file_format"] = file_format
        column_list = None
        batch_mem_size = 3000
        plan_str = "UploadPlan(file_path={}, \
            video_blob={}, \
            table_id={}, \
            batch_mem_size={}, \
            column_list={}, \
            file_options={})".format(
            file_path,
            "string of video blob",
            table_metainfo,
            batch_mem_size,
            column_list,
            file_options,
        )
        plan = UploadPlan(
            file_path,
            video_blob,
            table_metainfo,
            batch_mem_size,
            column_list,
            file_options,
        )
        self.assertEqual(plan.opr_type, PlanOprType.UPLOAD)
        self.assertEqual(plan.file_path, file_path)
        self.assertEqual(plan.video_blob, video_blob)
        self.assertEqual(plan.table_metainfo, table_metainfo)
        self.assertEqual(plan.batch_mem_size, batch_mem_size)

        self.assertEqual(str(plan), plan_str)

    def test_union_plan(self):
        all = True
        plan = UnionPlan(all)
        self.assertEqual(plan.opr_type, PlanOprType.UNION)
        self.assertEqual(plan.all, all)

    def test_create_materialized_view_plan(self):
        dummy_view = TableRef(TableInfo("dummy"))
        columns = ["id", "id2"]
        plan = CreateMaterializedViewPlan(dummy_view, columns)
        self.assertEqual(plan.opr_type, PlanOprType.CREATE_MATERIALIZED_VIEW)
        self.assertEqual(plan.view, dummy_view)
        self.assertEqual(plan.columns, columns)
