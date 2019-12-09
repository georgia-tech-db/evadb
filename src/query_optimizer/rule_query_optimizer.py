from expression.abstract_expression import ExpressionType
from expression.comparison_expression import ComparisonExpression
from expression.constant_value_expression import ConstantValueExpression
from query_planner.logical_projection_plan import LogicalProjectionPlan
from query_planner.logical_inner_join_plan import LogicalInnerJoinPlan
# from query_planner.logical_select_plan import LogicalSelectPlan
from query_planner.seq_scan_plan import SeqScanPlan
# from query_planner.video_table_plan import VideoTablePlan
from query_parser.table_ref import TableRef
from enum import Enum

from expression.tuple_value_expression import TupleValueExpression


class Rules(Enum):
    """Enum to encapsulate the list of rules we have available"""
    PREDICATE_PUSHDOWN = 1,
    PROJECTION_PUSHDOWN_SELECT = 2,
    PROJECTION_PUSHDOWN_JOIN= 3,
    SIMPLIFY_PREDICATE = 4,
    JOIN_ELIMINATION = 5,
    TRANSITIVE_CLOSURE = 6

class RuleQueryOptimizer:
    """Class to Encapsulate the functionality of the Rule Based Query Optimizer (Query Rewriter)"""
    def __init__(self):
        self.rule2value = {Rules.PREDICATE_PUSHDOWN: (self.predicate_pushdown, self.do_predicate_pushdown),
                           Rules.SIMPLIFY_PREDICATE: (self.simply_predicate, self.do_simplify_predicate),
                           Rules.TRANSITIVE_CLOSURE: (self.transitive_closure, self.do_transitive_closure),
                           Rules.PROJECTION_PUSHDOWN_SELECT: (self.projection_pushdown_select, self.do_projection_pushdown_select),
                           Rules.PROJECTION_PUSHDOWN_JOIN: (self.projection_pushdown_join, self.do_projection_pushdown_join),
                           Rules.JOIN_ELIMINATION: (self.join_elimination, self.do_join_elimination)}

    def run(self, root_node, rule_list):
        """ Runs the rule based Optimizer on the list of rules user selects

            Keyword Arguments:
            root_node -- The root node of the logical plan tree.
            rule_list -- The list containing rules user want to apply to the logical plan tree
                            (i.e. [Rules.PREDICATE_PUSHDOWN, Rules.SIMPLIFY_PREDICATE])

            :return: The modified logical tree (pointing the root node)
        """
        for rule in rule_list:
            self.traverse(root_node, rule)
        return root_node

    def traverse(self, curnode, rule):
        """ Recursive function that traverses the tree and applies all of the rules in the rule list

            Keyword Arguments:
            curnode -- Current node in the logical plan tree. Type will always be one of the Abstract Plan types.
            rule -- Rule applied to the current node.

            :return: Void
        """
        if type(curnode) == TableRef or type(curnode.children) == TableRef or len(curnode.children) == 0:
            return
        # for rule in rule_list:
        for child_ix, child in enumerate(curnode.children):
            func, condition = self.rule2value[rule]
            if condition(curnode, child):
                func(curnode, child_ix)
            self.traverse(child, rule)

    def predicate_pushdown(self, curnode, child_ix):
        """ Push down predicates so filters done as early as possible

            Keyword Arguments:
            curnode -- is the current node visited in the plan tree and is a type that inherits from the AbstractPlan type
            child_ix -- is an integer that represents the index of the child in the curnode's child list

            :return: Void
        """
        # curnode is the select and child is the join
        child = curnode.children[child_ix]
        # setting the parent's new child to be the join node
        curnode.parent.set_children([child])
        # setting the select's child to be after the join
        # find the join child with from the same video
        correct_ix = None
        curnode_tabnames = set([col.split('.')[0] for col in curnode.column_ids])
        vids = []
        for jc_ix, jc in enumerate(child.children):
            if type(jc) == TableRef:
                jc_tabnames = set([jc.table_info.table_name])
                vids = [jc.video]
            elif type(jc) == SeqScanPlan:
                jc_tabnames = set([attr.split('.')[0] for attr in jc.column_ids])
                vids = jc.videos
            elif type(jc) == LogicalInnerJoinPlan:
                jc_tabnames = set([attr.split('.')[0] for attr in jc.join_ids])
                vids = jc.videos
            else:
                return
            # getting all of the columns that the current node uses (other columns not in the join columns)
            if curnode_tabnames.issubset(jc_tabnames):
                correct_ix = jc_ix
                break
        if correct_ix is None:
            return

        # Set the videos because now, that we are below the join, we do not need both videos
        curnode.set_videos(vids)
        curnode.set_children([child.children[correct_ix]])
        child.children[correct_ix].parent = curnode
        # set the join's children to be the select
        child.children[correct_ix] = curnode
        child.parent = curnode.parent
        curnode.parent = child

    def projection_pushdown_select(self, curnode, child_ix):
        """ Push down projects so that we do not have unnecessary attributes

            Keyword Arguments:
            curnode -- is the current node visited in the plan tree and is a type that inherits from the AbstractPlan type
            child_ix -- is an integer that represents the index of the child in the curnode's child list

            :return: Void
        """
        # curnode is the projection
        # child is the select
        child = curnode.children[child_ix]
        # getting all of the columns that the current node uses (other columns not in the join columns)
        cols_project = [col for col in curnode.column_ids]
        # getting all of the columns that the select uses that are the same as it's child
        cols_select = [col for col in child.column_ids]
        cols_project.extend(cols_select)
        cols_project = list(set(cols_project))
        new_proj = LogicalProjectionPlan(videos=curnode.videos, column_ids=cols_project, foreign_column_ids=[])
        old_children = curnode.children[child_ix].children
        curnode.children[child_ix].set_children([new_proj])
        new_proj.set_children(old_children)
        for cc in old_children:
            cc.parent = new_proj
        # we did a previous select projection pushdown of the same columns
        # This means we need to push down further, and can delete the current node (the first projection)
        if type(child.parent) == LogicalProjectionPlan \
                and set(child.parent.column_ids) == set(new_proj.column_ids) \
                and curnode.parent is not None:
            cur_children = curnode.children
            curnode_ix = curnode.parent.children.index(curnode)
            curnode.parent.children[curnode_ix] = cur_children[0]
            cur_children[0].parent = curnode.parent

    def projection_pushdown_join(self, curnode, child_ix):
        """ Push down projects so that we do not have unnecessary attributes

        Keyword Arguments:
        curnode -- The current node visited in the plan tree and is a type that inherits from the AbstractPlan type
        child_ix -- An integer that represents the index of the child in the curnode's child list

        :return: Void
        """
        # curnode is the projection
        # child is the join
        child = curnode.children[child_ix]
        for cc_ix, cc in enumerate(child.children):
            if type(cc) == TableRef:
                cc_tabnames = [cc.table_info.table_name]
            elif type(cc) == LogicalInnerJoinPlan:
                cc_tabnames = [col.split('.')[0] for col in cc.join_ids]
            elif type(cc) == SeqScanPlan:
                cc_tabnames = [col.split('.')[0] for col in cc.column_ids]
            else:
                break
            # getting all of the columns that the join uses that are the same as it's child
            cols = [col for col in child.join_ids for tabname in cc_tabnames if tabname in col]
            # getting all of the columns that the current node uses (other columns not in the join columns)
            cols2 = [col for col in curnode.column_ids for tabname in cc_tabnames if tabname in col]
            cols.extend(cols2)
            # creating new Projection Node
            if type(cc) == TableRef:
                vids = [cc.video]
            else:
                vids = cc.videos
            new_proj1 = LogicalProjectionPlan(videos=vids, column_ids=list(set(cols)), foreign_column_ids=[])
            new_proj1.set_children([child.children[cc_ix]])
            new_proj1.parent = child
            child.children[cc_ix].parent = new_proj1
            child.children[cc_ix] = new_proj1

        # in this case, we have a join of three or more tables.
        # we already created a projection node in the previous recursive call of projection_pushdown_join
        # We can delete the projection in the middle between the joins
        if type(curnode.parent) == LogicalInnerJoinPlan:
            child.parent = curnode.parent
            curnode_ix = curnode.parent.children.index(curnode)
            curnode.parent.children[curnode_ix] = child

    def selective_first(self):
        """reorder predicates so that DBMS applies most selective first"""
        pass

    def simply_predicate(self, curnode, child_ix):
        """ Simplify predicate to remove unnecessary conditions (i.e.  1 = 0 or 0 = 0)

            Keyword Arguments:
            curnode -- The current node visited in the plan tree and is a type that inherits from the AbstractPlan type
            child_ix -- An integer that represents the index of the child in the curnode's child list

            :return: Void
        """
        boolean=curnode.predicate.evaluate()
        if not boolean:
            self.delete_node(curnode)

    def delete_node(self, curnode):
        """ Recreates the parent and child pointers to skip the sigma

           Keyword Arguments:
           curnode -- The current node visited in the plan tree and is a type that inherits from the AbstractPlan type

           :return: void
        """
        curnode.parent.set_children(curnode.children)
        for child in curnode.children:
            child.parent=curnode.parent

    def transitive_closure(self, curnode, child_ix):
        """ Ensures precise cardinality estimation when same predicate is being applied to both tables

            Keyword Arguments:
            curnode -- The current node visited in the plan tree and is a type that inherits from the AbstractPlan type
            child_ix -- An integer that represents the index of the child in the curnode's child list

            :return: void
        """
        child = curnode.children[child_ix]
        # checking if the current node is a comparison expression
        if type(curnode.predicate) == ComparisonExpression:
            const_idx = None
            col_tab_idx = None
            const_val = None
            if type(curnode.predicate.get_child(1)) == ConstantValueExpression:
                ##print ("R.H.S. Is constant val")
                const_idx = 1
                col_tab_idx = 0
            elif type(curnode.predicate.get_child(0)) == ConstantValueExpression:
                ##print ("L.H.S. is constant val")
                const_idx = 0
                col_tab_idx = 1
                
            # extracting the constant value from the predicate and table name and attribute
            const_val = curnode.predicate.get_child(const_idx).evaluate()
            selection_table = curnode.column_ids[0].split(".")[0]
            selection_column = curnode.column_ids[0].split(".")[1]
            
            # Now looking at the child
            join_cols = child.join_ids
            matched_join_idx = None
            for join_col_idx in range(len(join_cols)):
                if join_cols[join_col_idx] == curnode.column_ids[0]:
                    # remembering which of all the join columns matched with the parent selection column
                    matched_join_idx = join_col_idx 
            
            # If the columns did not matched
            if matched_join_idx == None:
                print ("Not possible")
                return 

            # checking supported types for grand child
            for gc_idx, gc in enumerate(child.children):
                if type(gc) == TableRef:
                    jc_tabnames = set([gc.table_info.table_name])
                    vids = [gc.video]
                elif type(gc) == SeqScanPlan:
                    jc_tabnames = set([attr.split('.')[0] for attr in gc.column_ids])
                    vids = gc.videos
                elif type(gc) == LogicalInnerJoinPlan:
                    jc_tabnames = set([attr.split('.')[0] for attr in gc.join_ids])
                    vids = gc.videos
                else:
                    print ("Grand child type is not suported")
                    return
    
                # Now calculate the join columns that are from jc_tablenames
                select_cols = []
                for c in join_cols:
                    if c.split(".")[0] in jc_tabnames:
                        select_cols.append(c)

                # For future improvement if multiple cols need to be added to selection, current implementation dont support that yet
                if len(select_cols) > 1:
                    return
                
                if len(select_cols) == 0:
                    continue 

                selected_col = select_cols[0]
                const = ConstantValueExpression(value=const_val)
                tup = TupleValueExpression(col_idx=int(selected_col.split('.')[1]))
                expression = ComparisonExpression(exp_type=ExpressionType.COMPARE_EQUAL, left=tup, right=const)
            
                # using both videos as purposely place "before" the join
                s1 = SeqScanPlan(predicate=expression, column_ids=[selected_col],
                                       videos=vids, foreign_column_ids=[])
                
                # parent of selection is join
                s1.parent = child 
                child.children[gc_idx] = s1
                s1.set_children([gc])
                # parent of grand child is now the newly added selection
                gc.parent = s1 

            # modifying the parent pointers after addition of the selection
            child.parent = curnode.parent
            curnode.parent.set_children([child])
        
        # setting the children and column ids
        child=curnode.children[child_ix]
        cur_col=curnode.column_ids

    def join_elimination(self, curnode, child_ix):
        """ Avoid unnecessary joins in case first table has foreign key constraint on the second table

            Keyword Arguments:
            curnode -- The current node visited in the plan tree and is a type that inherits from the AbstractPlan type
            child_ix -- An integer that represents the index of the child in the curnode's child list

            :return: void
        """
        child = curnode.children[child_ix]
        cur_col = curnode.column_ids
        foreign_col = curnode.foreign_column_ids
        foreign_col_id = curnode.foreign_column_ids[0].split(".")[1]
        cur_col_id = curnode.column_ids[0].split(".")[0]
        if foreign_col and cur_col[1] == foreign_col[0]:
            join = child.children
            grandchild = join[0].children[0]
            grandchild.parent = child
            new_expression = ConstantValueExpression(grandchild)
            child.set_predicate(new_expression)
            child.set_children([grandchild])
            child.set_foreign_column_ids([])
            curnode.set_foreign_column_ids([])
            new_pred = [curnode.column_ids[0], cur_col_id + "." + foreign_col_id]
            curnode.set_column_ids(new_pred)

    def do_projection_pushdown_join(self, curnode, child):
        """ Type of nodes required to perform projection pushdown with join node

            Keyword Arguments:
            curnode -- The current node visited in the plan tree and is a type that inherits from the AbstractPlan type
            child -- A child of curnode and is a type that inherits from the AbstractPlan type

            :return: Boolean value if given arguments are true or not
        """
        return type(curnode) == LogicalProjectionPlan and type(child) == LogicalInnerJoinPlan

    def do_projection_pushdown_select(self, curnode, child):
        """ Type of nodes required to perform projection pushdown with select node

            Keyword Arguments:
            curnode -- The current node visited in the plan tree and is a type that inherits from the AbstractPlan type
            child -- A child of curnode and is a type that inherits from the AbstractPlan type

            :return: Boolean value if given arguments are true or not
        """
        if type(child) != TableRef and len(child.children) > 0:
            joins = any([type(c) == LogicalInnerJoinPlan for c in child.children])
            return type(curnode) == LogicalProjectionPlan and type(child) == SeqScanPlan and not joins
        else:
            return type(curnode) == LogicalProjectionPlan and type(child) == SeqScanPlan

    def do_predicate_pushdown(self, curnode, child):
        """ Type of nodes required to perform prediate pushdown

            Keyword Arguments:
            curnode -- The current node visited in the plan tree and is a type that inherits from the AbstractPlan type
            child -- A child of curnode and is a type that inherits from the AbstractPlan type

            :return: Boolean value if given arguments are true or not
        """
        return type(curnode) == SeqScanPlan and type(child) == LogicalInnerJoinPlan

    def do_join_elimination(self, curnode, child):
        """ Type of nodes required to join elimination

            Keyword Arguments:
            curnode -- The current node visited in the plan tree and is a type that inherits from the AbstractPlan type
            child -- A child of curnode and is a type that inherits from the AbstractPlan type

            :return: Boolean value if given arguments are true or not
        """
        return type(curnode) == LogicalProjectionPlan and type(child) == SeqScanPlan \
               and type(child.children[0]) == LogicalInnerJoinPlan

    def do_simplify_predicate(self, curnode, child):
        """ Type of nodes required to perform simplify predicate

            Keyword Arguments:
            curnode -- The current node visited in the plan tree and is a type that inherits from the AbstractPlan type
            child -- A child of curnode and is a type that inherits from the AbstractPlan type

            :return: Boolean value if given arguments are true or not
        """
        return type(curnode) == SeqScanPlan


    def do_transitive_closure(self, curnode, child):
        """ Type of nodes required to perform transitive closure

            Keyword Arguments:
            curnode -- The current node visited in the plan tree and is a type that inherits from the AbstractPlan type
            child -- A child of curnode and is a type that inherits from the AbstractPlan type

            :return: Boolean value if given arguments are true or not
        """
        if type(curnode) == SeqScanPlan:
            if type(child) == LogicalInnerJoinPlan:
                return True
        '''
        if type(curnode) == LogicalProjectionPlan and type(child) == SeqScanPlan:
            if type(child.children[0]) == LogicalInnerJoinPlan:
                return True
        '''
        return False