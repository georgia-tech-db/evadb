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
from src.parser.table_ref import TableRef, TableInfo
from src.catalog.models.df_column import DataFrameColumn
from src.catalog.column_type import ColumnType
from src.catalog.catalog_manager import CatalogManager

from src.planner.create_plan import CreatePlan
from src.planner.insert_plan import InsertPlan
from src.planner.create_udf_plan import CreateUDFPlan
from src.planner.load_data_plan import LoadDataPlan
from src.planner.union_plan import UnionPlan
from src.planner.create_mat_view_plan import CreateMaterializedViewPlan
from src.planner.types import PlanOprType


class PlanNodeTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_create_plan(self):
        dummy_info = TableInfo('dummy')
        dummy_table = TableRef(dummy_info)

        CatalogManager().reset()
        columns = [DataFrameColumn('id', ColumnType.INTEGER),
                   DataFrameColumn('name', ColumnType.TEXT,
                                   array_dimensions=50)]
        dummy_plan_node = CreatePlan(dummy_table, columns, False)
        self.assertEqual(dummy_plan_node.opr_type, PlanOprType.CREATE)
        self.assertEqual(dummy_plan_node.if_not_exists, False)
        self.assertEqual(dummy_plan_node.video_ref.table_info.table_name,
                         "dummy")
        self.assertEqual(dummy_plan_node.column_list[0].name, "id")
        self.assertEqual(dummy_plan_node.column_list[1].name, "name")

    def test_insert_plan(self):
        video_id = 0
        column_ids = [0, 1]
        expression = type("AbstractExpression", (), {"evaluate": lambda: 1})
        values = [expression, expression]
        dummy_plan_node = InsertPlan(video_id, column_ids, values)
        self.assertEqual(dummy_plan_node.opr_type, PlanOprType.INSERT)

    def test_create_udf_plan(self):
        udf_name = 'udf'
        if_not_exists = True
        udfIO = 'udfIO'
        inputs = [udfIO, udfIO]
        outputs = [udfIO]
        impl_path = 'test'
        ty = 'classification'
        node = CreateUDFPlan(
            udf_name,
            if_not_exists,
            inputs,
            outputs,
            impl_path,
            ty)
        self.assertEqual(node.opr_type, PlanOprType.CREATE_UDF)
        self.assertEqual(node.if_not_exists, True)
        self.assertEqual(node.inputs, [udfIO, udfIO])
        self.assertEqual(node.outputs, [udfIO])
        self.assertEqual(node.impl_path, impl_path)
        self.assertEqual(node.udf_type, ty)

    def test_load_data_plan(self):
        table_metainfo = 'meta_info'
        file_path = 'test.mp4'
        plan_str = 'LoadDataPlan(table_id={},file_path={})'.format(
            table_metainfo, file_path)
        plan = LoadDataPlan(table_metainfo, file_path)
        self.assertEqual(plan.opr_type, PlanOprType.LOAD_DATA)
        self.assertEqual(plan.table_metainfo, table_metainfo)
        self.assertEqual(plan.file_path, file_path)
        self.assertEqual(str(plan), plan_str)

    def test_union_plan(self):
        all = True
        plan = UnionPlan(all)
        self.assertEqual(plan.opr_type, PlanOprType.UNION)
        self.assertEqual(plan.all, all)

    def test_create_materialized_view_plan(self):
        dummy_view = TableRef(TableInfo('dummy'))
        col_list = ['id', 'id2']
        query = 'Select id from MyVideo'
        plan = CreateMaterializedViewPlan(dummy_view, col_list, query)
        self.assertEqual(plan.opr_type, PlanOprType.CREATE_MATERIALIZED_VIEW)
        self.assertEqual(plan.view, dummy_view)
        self.assertEqual(plan.col_list, col_list)
        self.assertEqual(plan.query, query)
