import unittest
from unittest.mock import patch

from src.models.catalog.properties import VideoFormat
from src.models.catalog.video_info import VideoMetaInfo
from src.models.storage.batch import FrameBatch
from src.query_executor.plan_executor import PlanExecutor
from src.query_planner.seq_scan_plan import SeqScanPlan
from src.query_planner.storage_plan import StoragePlan


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

        root_abs_plan = SeqScanPlan(predicate=predicate)
        child_1_abs_plan = SeqScanPlan(predicate=predicate)
        child_2_abs_plan = SeqScanPlan(predicate=predicate)
        child_3_abs_plan = SeqScanPlan(predicate=predicate)
        child_1_1_abs_plan = SeqScanPlan(predicate=predicate)

        root_abs_plan.append_child(child_1_abs_plan)
        root_abs_plan.append_child(child_2_abs_plan)
        root_abs_plan.append_child(child_3_abs_plan)

        child_1_abs_plan.append_child(child_1_1_abs_plan)

        '''Build Execution Tree and check the nodes 
            are of the same type'''
        root_abs_executor = PlanExecutor(
            plan=root_abs_plan)._build_execution_tree(plan=root_abs_plan)

        # Root Nodes
        self.assertEqual(root_abs_plan.node_type,
                         root_abs_executor._node.node_type)

        # Children of Root
        for child_abs, child_exec in zip(root_abs_plan.children,
                                         root_abs_executor.children):
            self.assertEqual(child_abs.node_type, child_exec._node.node_type)
            # Grand Children of Root
            for gc_abs, gc_exec in zip(child_abs.children,
                                       child_exec.children):
                self.assertEqual(gc_abs.node_type, gc_exec._node.node_type)

    @patch(
        'src.query_executor.disk_based_storage_executor.SimpleVideoLoader')
    def test_should_return_the_new_path_after_execution(self, mock_class):
        class_instatnce = mock_class.return_value

        dummy_expr = type('dummy_expr', (),
                          {"evaluate": lambda x=None: [True, False,
                                                       True]})

        # Build plan tree
        video = VideoMetaInfo("dummy.avi", 10, VideoFormat.AVI)
        class_instatnce.load.return_value = map(lambda x: x, [
            FrameBatch([1, 2, 3], None),
            FrameBatch([4, 5, 6], None)])

        storage_plan = StoragePlan(video)
        seq_scan = SeqScanPlan(predicate=dummy_expr)
        seq_scan.append_child(storage_plan)

        # Execute the plan
        executor = PlanExecutor(seq_scan)
        actual = executor.execute_plan()
        expected = [
            FrameBatch([1, 3], None),
            FrameBatch([4, 6], None)]

        mock_class.assert_called_once()

        self.assertEqual(
            expected, actual
        )
