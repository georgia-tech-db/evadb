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
import pandas as pd
from pandas._testing import assert_frame_equal

import unittest
from unittest.mock import patch, MagicMock

from src.catalog.models.df_metadata import DataFrameMetadata
from src.executor.plan_executor import PlanExecutor
from src.models.storage.batch import Batch
from src.planner.seq_scan_plan import SeqScanPlan
from src.planner.storage_plan import StoragePlan
from src.planner.pp_plan import PPScanPlan
from src.planner.insert_plan import InsertPlan
from src.planner.create_plan import CreatePlan
from src.planner.create_udf_plan import CreateUDFPlan
from src.planner.load_data_plan import LoadDataPlan
from src.executor.load_executor import LoadDataExecutor
from src.executor.seq_scan_executor import SequentialScanExecutor
from src.executor.create_executor import CreateExecutor
from src.executor.create_udf_executor import CreateUDFExecutor
from src.executor.insert_executor import InsertExecutor
from src.executor.pp_executor import PPExecutor


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

        root_abs_plan = SeqScanPlan(predicate=predicate, column_ids=[])
        child_1_abs_plan = SeqScanPlan(predicate=predicate, column_ids=[])
        child_2_abs_plan = SeqScanPlan(predicate=predicate, column_ids=[])
        child_3_abs_plan = SeqScanPlan(predicate=predicate, column_ids=[])
        child_1_1_abs_plan = SeqScanPlan(predicate=predicate, column_ids=[])

        root_abs_plan.append_child(child_1_abs_plan)
        root_abs_plan.append_child(child_2_abs_plan)
        root_abs_plan.append_child(child_3_abs_plan)

        child_1_abs_plan.append_child(child_1_1_abs_plan)

        '''Build Execution Tree and check the nodes
            are of the same type'''
        root_abs_executor = PlanExecutor(
            plan=root_abs_plan)._build_execution_tree(plan=root_abs_plan)

        # Root Nodes
        self.assertEqual(root_abs_plan.opr_type,
                         root_abs_executor._node.opr_type)

        # Children of Root
        for child_abs, child_exec in zip(root_abs_plan.children,
                                         root_abs_executor.children):
            self.assertEqual(child_abs.opr_type, child_exec._node.opr_type)
            # Grand Children of Root
            for gc_abs, gc_exec in zip(child_abs.children,
                                       child_exec.children):
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
        plan = CreateUDFPlan('test', False, [], [], MagicMock(), None)
        executor = PlanExecutor(plan)._build_execution_tree(plan)
        self.assertIsInstance(executor, CreateUDFExecutor)

        # LoadDataExecutor
        plan = LoadDataPlan(MagicMock(), MagicMock())
        executor = PlanExecutor(plan)._build_execution_tree(plan)
        self.assertIsInstance(executor, LoadDataExecutor)

    @patch('src.executor.plan_executor.PlanExecutor._build_execution_tree')
    @patch('src.executor.plan_executor.PlanExecutor._clean_execution_tree')
    def test_execute_plan_for_seq_scan_plan(
            self, mock_clean, mock_build):

        # SequentialScanExecutor
        tree = MagicMock(node=SeqScanPlan(None, []))
        tree.exec.return_value = [
            Batch(pd.DataFrame([1])),
            Batch(pd.DataFrame([2])),
            Batch(pd.DataFrame([3]))]
        mock_build.return_value = tree

        actual = PlanExecutor(None).execute_plan()
        mock_build.assert_called_once_with(None)
        mock_clean.assert_called_once()
        tree.exec.assert_called_once()
        self.assertEqual(actual, Batch(pd.DataFrame([[1], [2], [3]])))

    @patch('src.executor.plan_executor.PlanExecutor._build_execution_tree')
    @patch('src.executor.plan_executor.PlanExecutor._clean_execution_tree')
    def test_execute_plan_for_pp_scan_plan(
            self, mock_clean, mock_build):
        # PPExecutor
        tree = MagicMock(node=PPScanPlan(None))
        tree.exec.return_value = [
            Batch(pd.DataFrame([1])),
            Batch(pd.DataFrame([2])),
            Batch(pd.DataFrame([3]))]
        mock_build.return_value = tree

        actual = PlanExecutor(None).execute_plan()
        mock_build.assert_called_once_with(None)
        mock_clean.assert_called_once()
        tree.exec.assert_called_once()
        self.assertEqual(actual, Batch(pd.DataFrame([[1], [2], [3]])))

    @patch('src.executor.plan_executor.PlanExecutor._build_execution_tree')
    @patch('src.executor.plan_executor.PlanExecutor._clean_execution_tree')
    @patch('src.executor.plan_executor.Batch')
    def test_execute_plan_for_create_insert_load_plans(
            self, mock_batch, mock_clean, mock_build):
        mock_batch.return_value = []

        # CreateExecutor
        tree = MagicMock(node=CreatePlan(None, [], False))
        mock_build.return_value = tree
        actual = PlanExecutor(None).execute_plan()
        tree.exec.assert_called_once()
        mock_batch.assert_called_once()
        assert_frame_equal(mock_batch.call_args[0][0], pd.DataFrame())
        mock_build.assert_called_once_with(None)
        mock_clean.assert_called_once()
        self.assertEqual(actual, [])

        # InsertExecutor
        mock_batch.reset_mock()
        mock_build.reset_mock()
        mock_clean.reset_mock()
        tree = MagicMock(node=InsertPlan(0, [], []))
        mock_build.return_value = tree
        actual = PlanExecutor(None).execute_plan()
        tree.exec.assert_called_once()
        mock_batch.assert_called_once()
        assert_frame_equal(mock_batch.call_args[0][0], pd.DataFrame())
        mock_build.assert_called_once_with(None)
        mock_clean.assert_called_once()
        self.assertEqual(actual, [])

        # CreateUDFExecutor
        mock_batch.reset_mock()
        mock_build.reset_mock()
        mock_clean.reset_mock()
        tree = MagicMock(node=CreateUDFPlan(None, False, [], [], None))
        mock_build.return_value = tree
        actual = PlanExecutor(None).execute_plan()
        tree.exec.assert_called_once()
        mock_batch.assert_called_once()
        assert_frame_equal(mock_batch.call_args[0][0], pd.DataFrame())
        mock_build.assert_called_once_with(None)
        mock_clean.assert_called_once()
        self.assertEqual(actual, [])

        # LoadDataExecutor
        mock_batch.reset_mock()
        mock_build.reset_mock()
        mock_clean.reset_mock()
        tree = MagicMock(node=LoadDataPlan(None, None))
        mock_build.return_value = tree
        actual = PlanExecutor(None).execute_plan()
        tree.exec.assert_called_once()
        mock_batch.assert_called_once()
        assert_frame_equal(mock_batch.call_args[0][0], pd.DataFrame())
        mock_build.assert_called_once_with(None)
        mock_clean.assert_called_once()
        self.assertEqual(actual, [])

    @unittest.skip("disk_based_storage_depricated")
    @patch('src.executor.disk_based_storage_executor.Loader')
    def test_should_return_the_new_path_after_execution(self, mock_class):
        class_instatnce = mock_class.return_value

        dummy_expr = type('dummy_expr', (),
                          {"evaluate": lambda x=None: [True, False,
                                                       True]})

        # Build plan tree
        video = DataFrameMetadata("dataset", "dummy.avi")
        batch_1 = Batch(pd.DataFrame({'data': [1, 2, 3]}))
        batch_2 = Batch(pd.DataFrame({'data': [4, 5, 6]}))
        class_instatnce.load.return_value = map(lambda x: x, [
            batch_1,
            batch_2])

        storage_plan = StoragePlan(video)
        seq_scan = SeqScanPlan(predicate=dummy_expr, column_ids=[])
        seq_scan.append_child(storage_plan)

        # Execute the plan
        executor = PlanExecutor(seq_scan)
        actual = executor.execute_plan()
        expected = batch_1[::2] + batch_2[::2]

        mock_class.assert_called_once()

        self.assertEqual(
            expected, actual
        )
