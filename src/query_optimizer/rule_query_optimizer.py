from query_planner.logical_projection_plan import LogicalProjectionPlan
from query_planner.logical_inner_join_plan import LogicalInnerJoinPlan
from query_planner.logical_select_plan import LogicalSelectPlan


class RuleQueryOptimizer:

    def run(self, plan_tree):
        curnode = plan_tree.root
        self.traverse(curnode)
        return plan_tree

    def traverse(self, curnode):
        if curnode.children == []:
            return
        for i, child in enumerate(curnode.children):
            if type(curnode) == LogicalSelectPlan:
                curnode.predicate = self.simply_predicate(curnode.predicate)
            # projection pushdown joins
            if type(curnode) == LogicalProjectionPlan and type(child) == LogicalInnerJoinPlan:
                self.projection_pushdown_join(curnode, child)
            # projection pushdown select
            if type(curnode) == LogicalProjectionPlan and type(child) == LogicalSelectPlan:
                self.projection_pushdown_select(curnode, i)
            # predicate pushdown
            if type(curnode) == LogicalSelectPlan and type(child) == LogicalInnerJoinPlan:
                self.predicate_pushdown(curnode, i)
            self.traverse(child)

    # push down predicates so filters done as early as possible
    def predicate_pushdown(self, curnode, child_ix):
        # curnode is the select and child is the join
        child = curnode.children[child_ix]
        # setting the parent's new child to be the join node
        curnode.parent.set_children([child])
        # setting the select's child to be after the join
        # find the join child with from the same video
        correct_ix = None
        for jc_ix, jc in enumerate(child.children):
            if jc.video == curnode.video:
                correct_ix = jc_ix
        curnode.set_children([child.children[correct_ix]])
        child.children[correct_ix].set_parent(curnode)
        # set the join's children to be the select
        child.children[correct_ix] = curnode
        child.parent = curnode.parent
        curnode.parent = child

    # push down projects so that we do not have unnecessary attributes
    def projection_pushdown_select(self, curnode, child_ix):
        # curnode is the projection
        # child is the select
        new_proj = LogicalProjectionPlan(video=curnode.video, column_ids=curnode.column_ids)
        old_children = curnode.children[child_ix].children
        curnode.children[child_ix].set_children([new_proj])
        new_proj.set_children(old_children)

    # TODO Refactor for new optimizer
    # push down projects so that we do not have unnecessary attributes
    def projection_pushdown_join(self, curnode, child):
        # curnode is the projection
        # child is the join
        #for c_ix, cc in enumerate(child.children):


        for tabname in child.children.keys():
            cols = [col for col in child.join_attrs if tabname in col]
            cols2 = [col for col in curnode.columns if tabname in col]
            cols.extend(cols2)
            new_proj1 = LogicalProjectionPlan(video=curnode.video, column_ids=cols)
            new_proj1._children = {tabname: child.children[tabname]}
            new_proj1._parent = child
            new_proj1.tablename = tabname
            child.children[new_proj1.tablename].parent = new_proj1
            child.children[new_proj1.tablename] = new_proj1

    # reorder predicates so that DBMS applies most selective first
    def selective_first(self, plan_tree):
        pass

    # No where clause like 1 = 0 or 0 = 0
    # Merging predicates
    def simply_predicate(self, pred):
        new_pred = pred
        return new_pred

    def join_elimination(self, plan_tree):
        pass