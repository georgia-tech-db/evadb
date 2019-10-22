# This is an interface between plan tree and execution tree.
# We traverse the plan tree and build execution tree from it

class PlanExecutor():
    __init__(self, AbstractPlan : plan):
        self.__plan = plan

    def __build_execution_tree(plan : AbstractPlan ) -> AbstractExecutor:
        """build the execution tree from plan tree
        
        Arguments:
            plan {AbstractPlan} -- Input Plan tree
        
        Returns:
            AbstractExecutor -- Compiled Execution tree
        """
        AbstractExecutor root = None
        if plan is None:
            return root
        
        ## Get plan node type

        plan_node_type = 



    def __clean_execution_tree(tree_root : AbstractExecutor):
        """clean the execution tree from memory
        
        Arguments:
            tree_root {AbstractExecutor} -- root of execution tree to delete
        """

    
    def execute_plan():
        """execute the plan tree
        
        """
        execution_tree = __build_execution_tree(self.__plan)

        ### do to

        __clean_execution_tree(execution_tree)

    
