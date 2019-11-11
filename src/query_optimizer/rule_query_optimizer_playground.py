# this is an implementation of a Rule Based Query Optimizer


class Node:
    def __init__(self, parent=None, value='', tablename='', children=[]):
        self.parent = parent
        self.children = {}
        self.value = value
        self.tablename = tablename

    def __str__(self, level=0):
        ret = "\t" * level + self.value + "\n"
        for child in self.children.values():
            ret += child.__str__(level + 1)
        return ret


class SelectNode(Node):
    def __init__(self, predicate=''):
        super(SelectNode, self).__init__()
        self.predicate = predicate
        self.value = 'sigma {}'.format(self.predicate)


class ProjectionNode(Node):
    def __init__(self, columns=[]):
        super(ProjectionNode, self).__init__()
        self.columns = columns
        self.value ='pi {}'.format(','.join(self.columns))


class JoinNode(Node):
    def __init__(self, tables=[], join_attrs=[]):
        super(JoinNode, self).__init__()
        self.columns = tables
        self.join_attrs = join_attrs
        pt1 = ' join '.join(tables)
        pt2 = ' = '.join(join_attrs)
        self.tablename = '_'.join(tables)
        self.value = '{}__{}'.format(pt1, pt2)


class LogicalPlanTree():
    def __init__(self):
        self.root = None

    def __str__(self, level=0):
        return str(self.root)


class RuleQueryOptimizer():
    def run(self, plan_tree):
        curnode = plan_tree.root
        self.traverse(curnode)
        return plan_tree

    def traverse(self, curnode):
        if curnode.children == {}:
            return
        for i, child in enumerate(curnode.children.values()):
            if type(curnode) == SelectNode:
                curnode.predicate = self.simply_predicate(curnode.predicate)
            # projection pushdown
            if type(curnode) == ProjectionNode and type(child) == JoinNode:
                self.projection_pushdown(curnode, child)
            # predicate pushdown
            if type(curnode) == SelectNode and type(child) == JoinNode:
                self.predicate_pushdown(curnode, child)

            self.traverse(child)

    # push down predicates so filters done as early as possible
    def predicate_pushdown(self, curnode, child):
        del curnode.parent.children[curnode.tablename]
        curnode.parent.children[child.tablename] = child
        del curnode.children[child.tablename]
        curnode.children[curnode.tablename] = child.children[curnode.tablename]
        child.children[curnode.tablename] = curnode
        child.parent = curnode.parent
        curnode.parent = child

    # push down projects so that we do not have unnecessary attributes
    def projection_pushdown(self, curnode, child):
        # curnode is the projection
        # child is the join

        for tabname in child.children.keys():
            cols = [col for col in child.join_attrs if tabname in col]
            cols2 = [col for col in curnode.columns if tabname in col]
            cols.extend(cols2)
            new_proj1 = ProjectionNode(columns=cols)
            new_proj1.children = {tabname: child.children[tabname]}
            new_proj1.parent = child
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


def test_predicate_push():
    print('Testing Predicate Pushdown')
    root = ProjectionNode(columns=['T1.time'])
    
    s1 = SelectNode(predicate='t=suv')
    s1.tablename = 'T1'
    s1.parent = root
    
    j1 = JoinNode(tables=['T1', 'T2'], join_attrs=['T1.t', 'T2.t'])
    j1.parent = s1
    
    t1 = Node(tablename='T1', value='T1')
    t2 = Node(tablename='T2', value='T2')
    
    s1.children = {j1.tablename: j1}
    t1.parent = j1
    t2.parent = j1
    
    j1.children = {t1.tablename: t1, t2.tablename: t2}
    root.children = {s1.tablename: s1}
    
    plan_tree = LogicalPlanTree()
    plan_tree.root = root
    print('Original Plan Tree')
    print(plan_tree)
    qo = RuleQueryOptimizer()
    new_tree = qo.run(plan_tree)
    print(new_tree)


def test_projection_push():
    print('testing projection pushdown')
    root = ProjectionNode(columns=['T1.name', 'T2.timestamp'])

    j1 = JoinNode(tables=['T1', 'T2'], join_attrs=['T1.t', 'T2.t'])
    j1.parent = root

    s1 = SelectNode(predicate='t=suv')
    s1.tablename = 'T2'
    s1.parent = j1

    t1 = Node(tablename='T1', value='T1')
    t2 = Node(tablename='T2', value='T2')

    s1.children = {t2.tablename: t2}
    t1.parent = j1
    t2.parent = s1

    j1.children = {t1.tablename: t1, s1.tablename: s1}
    root.children = {j1.tablename: j1}
    plan_tree = LogicalPlanTree()
    plan_tree.root = root
    print('Original Plan Tree')
    print(plan_tree)
    qo = RuleQueryOptimizer()
    new_tree = qo.run(plan_tree)
    print(new_tree)

    




if __name__ == '__main__':
    plan_tree = test_predicate_push()
    print('\n\n')
    plan_tree = test_projection_push()
