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

import pandas as pd

from evadb.catalog.catalog_type import TableType
from evadb.catalog.models.table_catalog import TableCatalogEntry
from evadb.executor.create_executor import CreateExecutor
from evadb.executor.create_udf_executor import CreateUDFExecutor
from evadb.executor.drop_object_executor import DropObjectExecutor, DropObjectPlan
from evadb.executor.insert_executor import InsertExecutor
from evadb.executor.load_executor import LoadDataExecutor
from evadb.executor.plan_executor import PlanExecutor
from evadb.executor.pp_executor import PPExecutor
from evadb.executor.seq_scan_executor import SequentialScanExecutor
from evadb.models.storage.batch import Batch
from evadb.plan_nodes.create_plan import CreatePlan
from evadb.plan_nodes.create_udf_plan import CreateUDFPlan
from evadb.plan_nodes.insert_plan import InsertPlan
from evadb.plan_nodes.load_data_plan import LoadDataPlan
from evadb.plan_nodes.pp_plan import PPScanPlan
from evadb.plan_nodes.rename_plan import RenamePlan
from evadb.plan_nodes.seq_scan_plan import SeqScanPlan
from evadb.plan_nodes.storage_plan import StoragePlan


class PlanExecutorTest(unittest.TestCase):
    def test_tree_structure_for_build_execution_tree(self):
        """
            Build an Abstract Plan with nodes:
         ß               root
                      /  |  \
                    c1   c2 c3
                    /
                   c1_1
        """

        predicate = None

        root_abs_plan = SeqScanPlan(predicate=predicate, columns=[])
        child_1_abs_plan = SeqScanPlan(predicate=predicate, columns=[])
        child_2_abs_plan = SeqScanPlan(predicate=predicate, columns=[])
        child_3_abs_plan = SeqScanPlan(predicate=predicate, columns=[])
        child_1_1_abs_plan = SeqScanPlan(predicate=predicate, columns=[])

        root_abs_plan.append_child(child_1_abs_plan)
        root_abs_plan.append_child(child_2_abs_plan)
        root_abs_plan.append_child(child_3_abs_plan)

        child_1_abs_plan.append_child(child_1_1_abs_plan)

        """Build Execution Tree and check the nodes
            are of the same type"""
        root_abs_executor = PlanExecutor(
            MagicMock(), plan=root_abs_plan
        )._build_execution_tree(plan=root_abs_plan)

        # Root Nodes
        self.assertEqual(root_abs_plan.opr_type, root_abs_executor._node.opr_type)

        # Children of Root
        for child_abs, child_exec in zip(
            root_abs_plan.children, root_abs_executor.children
        ):
            self.assertEqual(child_abs.opr_type, child_exec._node.opr_type)
            # Grand Children of Root
            for gc_abs, gc_exec in zip(child_abs.children, child_exec.children):
                self.assertEqual(gc_abs.opr_type, gc_exec._node.opr_type)

    def test_build_execution_tree_should_create_correct_exec_node(self):
        # SequentialScanExecutor
        plan = SeqScanPlan(MagicMock(), [])
        executor = PlanExecutor(MagicMock(), plan)._build_execution_tree(plan)
        self.assertIsInstance(executor, SequentialScanExecutor)

        # PPExecutor
        plan = PPScanPlan(MagicMock())
        executor = PlanExecutor(MagicMock(), plan)._build_execution_tree(plan)
        self.assertIsInstance(executor, PPExecutor)

        # CreateExecutor
        plan = CreatePlan(MagicMock(), [], False)
        executor = PlanExecutor(MagicMock(), plan)._build_execution_tree(plan)
        self.assertIsInstance(executor, CreateExecutor)

        # InsertExecutor
        plan = InsertPlan(0, [], [])
        executor = PlanExecutor(MagicMock(), plan)._build_execution_tree(plan)
        self.assertIsInstance(executor, InsertExecutor)

        # CreateUDFExecutor
        plan = CreateUDFPlan("test", False, [], [], MagicMock(), None)
        executor = PlanExecutor(MagicMock(), plan)._build_execution_tree(plan)
        self.assertIsInstance(executor, CreateUDFExecutor)

        # DropObjectExecutor
        plan = DropObjectPlan(MagicMock(), "test", False)
        executor = PlanExecutor(MagicMock(), plan)._build_execution_tree(plan)
        self.assertIsInstance(executor, DropObjectExecutor)

        # LoadDataExecutor
        plan = LoadDataPlan(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()
        )
        executor = PlanExecutor(MagicMock(), plan)._build_execution_tree(plan)
        self.assertIsInstance(executor, LoadDataExecutor)

    @patch("evadb.executor.plan_executor.PlanExecutor._build_execution_tree")
    def test_execute_plan_for_seq_scan_plan(self, mock_build):
        batch_list = [
            Batch(pd.DataFrame([1])),
            Batch(pd.DataFrame([2])),
            Batch(pd.DataFrame([3])),
        ]

        # SequentialScanExecutor
        tree = MagicMock(node=SeqScanPlan(None, []))
        tree.exec.return_value = batch_list
        mock_build.return_value = tree

        actual = list(PlanExecutor(MagicMock(), None).execute_plan())
        mock_build.assert_called_once_with(None)

        tree.exec.assert_called_once()
        self.assertEqual(actual, batch_list)

    @patch("evadb.executor.plan_executor.PlanExecutor._build_execution_tree")
    def test_execute_plan_for_pp_scan_plan(self, mock_build):
        batch_list = [
            Batch(pd.DataFrame([1])),
            Batch(pd.DataFrame([2])),
            Batch(pd.DataFrame([3])),
        ]
        # PPExecutor
        tree = MagicMock(node=PPScanPlan(None))
        tree.exec.return_value = batch_list
        mock_build.return_value = tree

        actual = list(PlanExecutor(MagicMock(), None).execute_plan())
        mock_build.assert_called_once_with(None)

        tree.exec.assert_called_once()
        self.assertEqual(actual, batch_list)

    @patch("evadb.executor.plan_executor.PlanExecutor._build_execution_tree")
    def test_execute_plan_for_create_insert_load_upload_plans(self, mock_build):
        # CreateExecutor
        tree = MagicMock(node=CreatePlan(None, [], False))
        mock_build.return_value = tree
        actual = list(PlanExecutor(MagicMock(), None).execute_plan())
        tree.exec.assert_called_once()
        mock_build.assert_called_once_with(None)

        self.assertEqual(actual, [])

        # InsertExecutor
        mock_build.reset_mock()

        tree = MagicMock(node=InsertPlan(0, [], []))
        mock_build.return_value = tree
        actual = list(PlanExecutor(MagicMock(), None).execute_plan())
        tree.exec.assert_called_once()
        mock_build.assert_called_once_with(None)

        self.assertEqual(actual, [])

        # CreateUDFExecutor
        mock_build.reset_mock()

        tree = MagicMock(node=CreateUDFPlan(None, False, [], [], None))
        mock_build.return_value = tree
        actual = list(PlanExecutor(MagicMock(), None).execute_plan())
        tree.exec.assert_called_once()
        mock_build.assert_called_once_with(None)

        self.assertEqual(actual, [])

        # LoadDataExecutor
        mock_build.reset_mock()

        tree = MagicMock(node=LoadDataPlan(None, None, None, None, None))
        mock_build.return_value = tree
        actual = list(PlanExecutor(MagicMock(), None).execute_plan())
        tree.exec.assert_called_once()
        mock_build.assert_called_once_with(None)

        self.assertEqual(actual, [])

    @patch("evadb.executor.plan_executor.PlanExecutor._build_execution_tree")
    def test_execute_plan_for_rename_plans(self, mock_build):
        # RenameExecutor
        tree = MagicMock(node=RenamePlan(None, None))
        mock_build.return_value = tree
        actual = list(PlanExecutor(MagicMock(), None).execute_plan())
        tree.exec.assert_called_once()
        mock_build.assert_called_once_with(None)

        self.assertEqual(actual, [])

    @patch("evadb.executor.plan_executor.PlanExecutor._build_execution_tree")
    def test_execute_plan_for_drop_plans(self, mock_build):
        # DropExecutor
        tree = MagicMock(node=DropObjectPlan(None, None, None))
        mock_build.return_value = tree
        actual = list(PlanExecutor(MagicMock(), None).execute_plan())
        tree.exec.assert_called_once()
        mock_build.assert_called_once_with(None)

        self.assertEqual(actual, [])

    @unittest.skip("disk_based_storage_deprecated")
    @patch("evadb.executor.disk_based_storage_executor.Loader")
    def test_should_return_the_new_path_after_execution(self, mock_class):
        class_instance = mock_class.return_value

        dummy_expr = type(
            "dummy_expr", (), {"evaluate": lambda x=None: [True, False, True]}
        )

        # Build plan tree
        video = TableCatalogEntry("dataset", "dummy.avi", table_type=TableType.VIDEO)
        batch_1 = Batch(pd.DataFrame({"data": [1, 2, 3]}))
        batch_2 = Batch(pd.DataFrame({"data": [4, 5, 6]}))
        class_instance.load.return_value = map(lambda x: x, [batch_1, batch_2])

        storage_plan = StoragePlan(video, batch_mem_size=3000)
        seq_scan = SeqScanPlan(predicate=dummy_expr, column_ids=[])
        seq_scan.append_child(storage_plan)

        # Execute the plan
        executor = PlanExecutor(seq_scan)
        actual = executor.execute_plan()
        expected = batch_1[::2] + batch_2[::2]

        mock_class.assert_called_once()

        self.assertEqual(expected, actual)
