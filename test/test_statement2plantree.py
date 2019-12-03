import unittest
from query_optimizer.statement2plantree import Statement2Plantree
from src.query_parser.eva_parser import EvaFrameQLParser
from query_planner.logical_select_plan import LogicalSelectPlan
from query_planner.logical_inner_join_plan import LogicalInnerJoinPlan
from query_planner.logical_projection_plan import LogicalProjectionPlan
from query_planner.video_table_plan import VideoTablePlan


class RuleQueryOptimizerTest(unittest.TestCase):

    def test_simple_select(self):
        parser = EvaFrameQLParser()
        query = "SELECT CLASS FROM TAIPAI;"
        eva_statement_list = parser.parse(query)
        plan_tree = Statement2Plantree.convert(eva_statement_list[0])
        self.assertIsNone(plan_tree.parent)
        self.assertTrue(type(plan_tree), LogicalSelectPlan)
        self.assertTrue(len(plan_tree.children) == 1)
        self.assertTrue(type(plan_tree.children[0]) == VideoTablePlan)
        self.assertTrue(len(plan_tree.children[0]) == 0)

    def test_simple_where(self):
        pass
