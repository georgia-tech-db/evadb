import unittest
from query_optimizer.statement2plantree import Statement2Plantree
from src.query_parser.eva_parser import EvaFrameQLParser
# from query_planner.logical_select_plan import LogicalSelectPlan
from query_planner.seq_scan_plan import SeqScanPlan
# from query_planner.video_table_plan import VideoTablePlan
from query_parser.table_ref import TableRef


# Test cases to test if we can go from SQL statement to logical plan tree
class TestStatement2PlanTree(unittest.TestCase):

    # Tests a Simple Select Statement with no Where clause
    def test_simple_select(self):
        parser = EvaFrameQLParser()
        query = "SELECT CLASS FROM TAIPAI;"
        eva_statement_list = parser.parse(query)
        plan_tree = Statement2Plantree.convert(eva_statement_list)
        self.assertIsNone(plan_tree.parent)
        self.assertTrue(type(plan_tree), SeqScanPlan)
        self.assertTrue(len(plan_tree.children) == 1)
        self.assertTrue(type(plan_tree.children[0]) == TableRef)

    # Test a select statement with where clause
    def test_simple_where(self):
        parser = EvaFrameQLParser()
        query = "SELECT CLASS FROM TAIPAI WHERE CLASS='First';"
        eva_statement_list = parser.parse(query)
        plan_tree = Statement2Plantree.convert(eva_statement_list)
    
        self.assertIsNone(plan_tree.parent)
        self.assertEqual(type(plan_tree.children), SeqScanPlan)
        self.assertTrue('CLASS' in plan_tree.children.column_ids)

    # Todo select statement with join clause
    def test_simple_join(self):
        pass

