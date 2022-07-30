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
from unittest.mock import MagicMock

from mock import patch

from eva.executor.create_mat_view_executor import CreateMaterializedViewExecutor
from eva.parser.table_ref import TableInfo, TableRef
from eva.planner.create_mat_view_plan import CreateMaterializedViewPlan
from eva.planner.types import PlanOprType


class CreateMaterializedExecutorTest(unittest.TestCase):
    @patch("eva.executor.create_mat_view_executor.handle_if_not_exists")
    def test_support_only_seq_scan(self, mock_check):
        mock_check.return_value = False
        dummy_view = TableRef(TableInfo("dummy"))
        columns = ["id", "id2"]
        plan = CreateMaterializedViewPlan(dummy_view, columns)
        for child_opr_type in PlanOprType:
            if child_opr_type is PlanOprType.SEQUENTIAL_SCAN:
                continue
            child = MagicMock()
            child.node.opr_type = child_opr_type
            with self.assertRaises(RuntimeError):
                create_udf_executor = CreateMaterializedViewExecutor(plan)
                create_udf_executor.append_child(child)
                create_udf_executor.exec()

    @patch("eva.executor.create_mat_view_executor.handle_if_not_exists")
    def test_raises_mismatch_columns(self, mock_check):
        mock_check.return_value = False
        dummy_view = TableRef(TableInfo("dummy"))
        columns = ["id", "id2"]
        plan = CreateMaterializedViewPlan(dummy_view, columns)
        child = MagicMock()
        child.node.opr_type = PlanOprType.SEQUENTIAL_SCAN
        child.project_expr.__len__.return_value = 3
        with self.assertRaises(RuntimeError):
            create_udf_executor = CreateMaterializedViewExecutor(plan)
            create_udf_executor.append_child(child)
            create_udf_executor.exec()
