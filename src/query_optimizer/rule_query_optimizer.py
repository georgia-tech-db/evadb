from expression.constant_value_expression import ConstantValueExpression
from query_planner.logical_projection_plan import LogicalProjectionPlan
from query_planner.logical_inner_join_plan import LogicalInnerJoinPlan
from query_planner.logical_select_plan import LogicalSelectPlan
from query_planner.video_table_plan import VideoTablePlan
from enum import Enum


# Enum to encapsulate the list of rules we have available
class Rules(Enum):
    PREDICATE_PUSHDOWN = 1,
    PROJECTION_PUSHDOWN_SELECT = 2,
    PROJECTION_PUSHDOWN_JOIN= 3,
    SIMPLIFY_PREDICATE = 4,
    JOIN_ELIMINATION = 5


# Class to Encapsulate the functionality of the Rule Based Query Optimizer (Query Rewriter)
class RuleQueryOptimizer:
    def __init__(self):
        self.rule2value = {Rules.PREDICATE_PUSHDOWN: (self.predicate_pushdown, self.do_predicate_pushdown),
                           Rules.SIMPLIFY_PREDICATE: (self.simply_predicate, self.do_simplify_predicate),
                           Rules.PROJECTION_PUSHDOWN_SELECT: (self.projection_pushdown_select, self.do_projection_pushdown_select),
                           Rules.PROJECTION_PUSHDOWN_JOIN: (self.projection_pushdown_join, self.do_projection_pushdown_join),
                           Rules.JOIN_ELIMINATION: (self.join_elimination, self.do_join_elimination)}


    # Runs the rule based Optimizer on the list of rules you want
    # rule_list : a list of Rule Enums. The rules will be ran in the order specified.
    #             example: [Rules.PREDICATE_PUSHDOWN, Rules.SIMPLIFY_PREDICATE]
    def run(self, root_node, rule_list):
        for rule in rule_list:
            self.traverse(root_node, rule)
        return root_node

    # Recursive function that traverses the tree and applies all of the rules in the rule list
    # curnode : is the current node visited in the plan tree and is a type that inherits from the AbstractPlan type
    def traverse(self, curnode, rule):
        if type(curnode.children) == VideoTablePlan or len(curnode.children) == 0:
            return
        # for rule in rule_list:
        for child_ix, child in enumerate(curnode.children):
            func, condition = self.rule2value[rule]
            if condition(curnode, child):
                func(curnode, child_ix)
            self.traverse(child, rule)

    # push down predicates so filters done as early as possible
    # curnode : is the current node visited in the plan tree and is a type that inherits from the AbstractPlan type
    # child_ix : is an integer that represents the index of the child in the curnode's child list
    def predicate_pushdown(self, curnode, child_ix):
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
            if type(jc) == VideoTablePlan:
                jc_tabnames = set([jc.tablename])
                vids = [jc.video]
            elif type(jc) == LogicalSelectPlan:
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

    # push down projects so that we do not have unnecessary attributes
    # curnode : is the current node visited in the plan tree and is a type that inherits from the AbstractPlan type
    # child_ix : is an integer that represents the index of the child in the curnode's child list
    def projection_pushdown_select(self, curnode, child_ix):
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

    # push down projects so that we do not have unnecessary attributes
    # curnode : is the current node visited in the plan tree and is a type that inherits from the AbstractPlan type
    # child_ix : is an integer that represents the index of the child in the curnode's child list
    def projection_pushdown_join(self, curnode, child_ix):
        # curnode is the projection
        # child is the join
        child = curnode.children[child_ix]
        for cc_ix, cc in enumerate(child.children):
            if type(cc) == VideoTablePlan:
                cc_tabnames = [cc.tablename]
            elif type(cc) == LogicalInnerJoinPlan:
                cc_tabnames = [col.split('.')[0] for col in cc.join_ids]
            elif type(cc) == LogicalSelectPlan:
                cc_tabnames = [col.split('.')[0] for col in cc.column_ids]
            else:
                break
            # getting all of the columns that the join uses that are the same as it's child
            cols = [col for col in child.join_ids for tabname in cc_tabnames if tabname in col]
            # getting all of the columns that the current node uses (other columns not in the join columns)
            cols2 = [col for col in curnode.column_ids for tabname in cc_tabnames if tabname in col]
            cols.extend(cols2)
            # creating new Projection Node
            if type(cc) == VideoTablePlan:
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

    # reorder predicates so that DBMS applies most selective first
    def selective_first(self):
        pass

    # No where clause like 1 = 0 or 0 = 0
    # Merging predicates
    # pred will be an AbstractExpression type
    def simply_predicate(self, curnode, child_ix):
        boolean=curnode.predicate.evaluate()
        if not boolean:
            self.delete_node(curnode)

    #curnode : 
    def delete_node(self, curnode):
        curnode.parent.set_children(curnode.children)
        for child in curnode.children:
            child.parent=curnode.parent
        
    # curnode : is the current node visited in the plan tree and is a type that inherits from the AbstractPlan type
    # child_ix : is an integer that represents the index of the child in the curnode's child list
    def join_elimination(self, curnode, child_ix):
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

    # curnode : is the current node visited in the plan tree and is a type that inherits from the AbstractPlan type
    # child : is a child of curnode and is a type that inherits from the AbstractPlan type
    def do_projection_pushdown_join(self, curnode, child):
        return type(curnode) == LogicalProjectionPlan and type(child) == LogicalInnerJoinPlan

    # curnode : is the current node visited in the plan tree and is a type that inherits from the AbstractPlan type
    # child : is a child of curnode and is a type that inherits from the AbstractPlan type
    def do_projection_pushdown_select(self, curnode, child):
        if len(child.children) > 0:
            joins = any([type(c) == LogicalInnerJoinPlan for c in child.children])
            return type(curnode) == LogicalProjectionPlan and type(child) == LogicalSelectPlan and not joins
        else:
            return type(curnode) == LogicalProjectionPlan and type(child) == LogicalSelectPlan

    # curnode : is the current node visited in the plan tree and is a type that inherits from the AbstractPlan type
    # child : is a child of curnode and is a type that inherits from the AbstractPlan type
    def do_predicate_pushdown(self, curnode, child):
        return type(curnode) == LogicalSelectPlan and type(child) == LogicalInnerJoinPlan

    # curnode : is the current node visited in the plan tree and is a type that inherits from the AbstractPlan type
    # child : is a child of curnode and is a type that inherits from the AbstractPlan type
    def do_join_elimination(self, curnode, child):
        return type(curnode) == LogicalProjectionPlan and type(child) == LogicalSelectPlan \
               and type(child.children[0]) == LogicalInnerJoinPlan

    # curnode : is the current node visited in the plan tree and is a type that inherits from the AbstractPlan type
    # child : is a child of curnode and is a type that inherits from the AbstractPlan type
    def do_simplify_predicate(self, curnode, child):
        return type(curnode) == LogicalSelectPlan

