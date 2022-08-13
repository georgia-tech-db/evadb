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

import pandas as pd

from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.executor.create_executor import CreateExecutor
from eva.executor.create_udf_executor import CreateUDFExecutor
from eva.executor.drop_udf_executor import DropUDFExecutor
from eva.executor.insert_executor import InsertExecutor
from eva.executor.load_executor import LoadDataExecutor
from eva.executor.plan_executor import PlanExecutor
from eva.executor.pp_executor import PPExecutor
from eva.executor.seq_scan_executor import SequentialScanExecutor
from eva.executor.upload_executor import UploadExecutor
from eva.models.storage.batch import Batch
from eva.planner.create_plan import CreatePlan
from eva.planner.create_udf_plan import CreateUDFPlan
from eva.planner.drop_plan import DropPlan
from eva.planner.drop_udf_plan import DropUDFPlan
from eva.planner.insert_plan import InsertPlan
from eva.planner.load_data_plan import LoadDataPlan
from eva.planner.pp_plan import PPScanPlan
from eva.planner.rename_plan import RenamePlan
from eva.planner.seq_scan_plan import SeqScanPlan
from eva.planner.storage_plan import StoragePlan
from eva.planner.upload_plan import UploadPlan


class PlanExecutorTest(unittest.TestCase):
    def test_tree_structure_for_build_execution_tree(self):
        """
            Build an Abastract Plan with nodes:
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
        root_abs_executor = PlanExecutor(plan=root_abs_plan)._build_execution_tree(
            plan=root_abs_plan
        )

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
        executor = PlanExecutor(plan)._build_execution_tree(plan)
        self.assertIsInstance(executor, SequentialScanExecutor)

        # PPExecutor
        plan = PPScanPlan(MagicMock())
        executor = PlanExecutor(plan)._build_execution_tree(plan)
        self.assertIsInstance(executor, PPExecutor)

        # CreateExecutor
        plan = CreatePlan(MagicMock(), [], False)
        executor = PlanExecutor(plan)._build_execution_tree(plan)
        self.assertIsInstance(executor, CreateExecutor)

        # InsertExecutor
        plan = InsertPlan(0, [], [])
        executor = PlanExecutor(plan)._build_execution_tree(plan)
        self.assertIsInstance(executor, InsertExecutor)

        # CreateUDFExecutor
        plan = CreateUDFPlan("test", False, [], [], MagicMock(), None)
        executor = PlanExecutor(plan)._build_execution_tree(plan)
        self.assertIsInstance(executor, CreateUDFExecutor)

        # DropUDFExecutor
        plan = DropUDFPlan("test", False)
        executor = PlanExecutor(plan)._build_execution_tree(plan)
        self.assertIsInstance(executor, DropUDFExecutor)

        # LoadDataExecutor
        plan = LoadDataPlan(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()
        )
        executor = PlanExecutor(plan)._build_execution_tree(plan)
        self.assertIsInstance(executor, LoadDataExecutor)

        plan = UploadPlan(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()
        )
        executor = PlanExecutor(plan)._build_execution_tree(plan)
        self.assertIsInstance(executor, UploadExecutor)

    @patch("eva.executor.plan_executor.PlanExecutor._build_execution_tree")
    @patch("eva.executor.plan_executor.PlanExecutor._clean_execution_tree")
    def test_execute_plan_for_seq_scan_plan(self, mock_clean, mock_build):

        batch_list = [
            Batch(pd.DataFrame([1])),
            Batch(pd.DataFrame([2])),
            Batch(pd.DataFrame([3])),
        ]

        # SequentialScanExecutor
        tree = MagicMock(node=SeqScanPlan(None, []))
        tree.exec.return_value = batch_list
        mock_build.return_value = tree

        actual = list(PlanExecutor(None).execute_plan())
        mock_build.assert_called_once_with(None)
        mock_clean.assert_called_once()
        tree.exec.assert_called_once()
        self.assertEqual(actual, batch_list)

    @patch("eva.executor.plan_executor.PlanExecutor._build_execution_tree")
    @patch("eva.executor.plan_executor.PlanExecutor._clean_execution_tree")
    def test_execute_plan_for_pp_scan_plan(self, mock_clean, mock_build):

        batch_list = [
            Batch(pd.DataFrame([1])),
            Batch(pd.DataFrame([2])),
            Batch(pd.DataFrame([3])),
        ]
        # PPExecutor
        tree = MagicMock(node=PPScanPlan(None))
        tree.exec.return_value = batch_list
        mock_build.return_value = tree

        actual = list(PlanExecutor(None).execute_plan())
        mock_build.assert_called_once_with(None)
        mock_clean.assert_called_once()
        tree.exec.assert_called_once()
        self.assertEqual(actual, batch_list)

    @patch("eva.executor.plan_executor.PlanExecutor._build_execution_tree")
    @patch("eva.executor.plan_executor.PlanExecutor._clean_execution_tree")
    def test_execute_plan_for_create_insert_load_upload_plans(
        self, mock_clean, mock_build
    ):

        # CreateExecutor
        tree = MagicMock(node=CreatePlan(None, [], False))
        mock_build.return_value = tree
        actual = list(PlanExecutor(None).execute_plan())
        tree.exec.assert_called_once()
        mock_build.assert_called_once_with(None)
        mock_clean.assert_called_once()
        self.assertEqual(actual, [])

        # InsertExecutor
        mock_build.reset_mock()
        mock_clean.reset_mock()
        tree = MagicMock(node=InsertPlan(0, [], []))
        mock_build.return_value = tree
        actual = list(PlanExecutor(None).execute_plan())
        tree.exec.assert_called_once()
        mock_build.assert_called_once_with(None)
        mock_clean.assert_called_once()
        self.assertEqual(actual, [])

        # CreateUDFExecutor
        mock_build.reset_mock()
        mock_clean.reset_mock()
        tree = MagicMock(node=CreateUDFPlan(None, False, [], [], None))
        mock_build.return_value = tree
        actual = list(PlanExecutor(None).execute_plan())
        tree.exec.assert_called_once()
        mock_build.assert_called_once_with(None)
        mock_clean.assert_called_once()
        self.assertEqual(actual, [])

        # LoadDataExecutor
        mock_build.reset_mock()
        mock_clean.reset_mock()
        tree = MagicMock(node=LoadDataPlan(None, None, None, None, None))
        mock_build.return_value = tree
        actual = list(PlanExecutor(None).execute_plan())
        tree.exec.assert_called_once()
        mock_build.assert_called_once_with(None)
        mock_clean.assert_called_once()
        self.assertEqual(actual, [])

        # UploadExecutor
        mock_build.reset_mock()
        mock_clean.reset_mock()
        tree = MagicMock(node=UploadPlan(None, None, None, None, None, None))
        mock_build.return_value = tree
        actual = list(PlanExecutor(None).execute_plan())
        tree.exec.assert_called_once()
        mock_build.assert_called_once_with(None)
        mock_clean.assert_called_once()
        self.assertEqual(actual, [])

    @patch("eva.executor.plan_executor.PlanExecutor._build_execution_tree")
    @patch("eva.executor.plan_executor.PlanExecutor._clean_execution_tree")
    def test_execute_plan_for_rename_plans(self, mock_clean, mock_build):

        # RenameExecutor
        tree = MagicMock(node=RenamePlan(None, None))
        mock_build.return_value = tree
        actual = list(PlanExecutor(None).execute_plan())
        tree.exec.assert_called_once()
        mock_build.assert_called_once_with(None)
        mock_clean.assert_called_once()
        self.assertEqual(actual, [])

    @patch("eva.executor.plan_executor.PlanExecutor._build_execution_tree")
    @patch("eva.executor.plan_executor.PlanExecutor._clean_execution_tree")
    def test_execute_plan_for_drop_plans(self, mock_clean, mock_build):

        # DropExecutor
        tree = MagicMock(node=DropPlan(None, None))
        mock_build.return_value = tree
        actual = list(PlanExecutor(None).execute_plan())
        tree.exec.assert_called_once()
        mock_build.assert_called_once_with(None)
        mock_clean.assert_called_once()
        self.assertEqual(actual, [])

        # DropUDFExecutor
        mock_build.reset_mock()
        mock_clean.reset_mock()
        tree = MagicMock(node=DropUDFPlan(None, False))
        mock_build.return_value = tree
        actual = list(PlanExecutor(None).execute_plan())
        tree.exec.assert_called_once()
        mock_build.assert_called_once_with(None)
        mock_clean.assert_called_once()
        self.assertEqual(actual, [])

    @unittest.skip("disk_based_storage_depricated")
    @patch("eva.executor.disk_based_storage_executor.Loader")
    def test_should_return_the_new_path_after_execution(self, mock_class):
        class_instatnce = mock_class.return_value

        dummy_expr = type(
            "dummy_expr", (), {"evaluate": lambda x=None: [True, False, True]}
        )

        # Build plan tree
        video = DataFrameMetadata("dataset", "dummy.avi")
        batch_1 = Batch(pd.DataFrame({"data": [1, 2, 3]}))
        batch_2 = Batch(pd.DataFrame({"data": [4, 5, 6]}))
        class_instatnce.load.return_value = map(lambda x: x, [batch_1, batch_2])

        storage_plan = StoragePlan(video, batch_mem_size=3000)
        seq_scan = SeqScanPlan(predicate=dummy_expr, column_ids=[])
        seq_scan.append_child(storage_plan)

        # Execute the plan
        executor = PlanExecutor(seq_scan)
        actual = executor.execute_plan()
        expected = batch_1[::2] + batch_2[::2]

        mock_class.assert_called_once()

        self.assertEqual(expected, actual)
