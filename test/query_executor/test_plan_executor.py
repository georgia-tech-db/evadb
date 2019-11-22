import unittest

from src.query_planner.seq_scan_plan import SeqScanPlan
from src.query_executor.plan_executor import PlanExecutor


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
