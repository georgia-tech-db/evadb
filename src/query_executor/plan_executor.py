from src.query_planner.abstract_plan import AbstractPlan
from src.query_executor.abstract_executor import AbstractExecutor
from src.planner.types import NodeType
from src.query_executor.seq_scan_executor import SequentialScanExecutor


# This is an interface between plan tree and execution tree.
# We traverse the plan tree and build execution tree from it
# select * from video where label = car
class PlanExecutor():
    def __init__(self, plan: AbstractPlan):
        self._plan = plan

    def _build_execution_tree(self, plan: AbstractPlan) -> AbstractExecutor:
        """build the execution tree from plan tree
        
        Arguments:
            plan {AbstractPlan} -- Input Plan tree
        
        Returns:
            AbstractExecutor -- Compiled Execution tree
        """
        root = None
        if plan is None:
            return root


        
        ## Get plan node type
        plan_node_type = plan.node_type
        if plan_node_type == NodeType.SEQUENTIAL_SCAN_TYPE:
            executor_node = SequentialScanExecutor(None, node=plan)
        elif plan_node_type == NodeType.PP_FILTER_TYPE:
            pass 

        # ToDo recursively build execution tree based on node type      
        for children in plan.children:
            executor_node.append_child(self._build_execution_tree(children))
        
        return executor_node
      
      




    def _clean_execution_tree(self, tree_root: AbstractExecutor):
        """clean the execution tree from memory
        
        Arguments:
            tree_root {AbstractExecutor} -- root of execution tree to delete
        """
        # ToDo
        # clear all the nodes from the execution tree

    def execute_plan(self):
        """execute the plan tree
        
        """
        execution_tree = self._build_execution_tree(self._plan)

        ### ToDo
        output_batches = []

        '''
        for child in execution_tree.children:
            while (batch = child.next() != None:
            output_batches.append(batch)
        '''

        self._clean_execution_tree(execution_tree)
