# this is an implementation of a Rule Based Query Optimizer


# class that represents a generic node in the logical plan tree
# This will mostly be used for the table nodes
class Node:
    # Parent: Node type
    # value: Used as the "to-string" representation
    # children: List of Node objects
    def __init__(self, parent=None, value='', tablename='', children=[]):
        self.parent = parent
        self.children = {}
        self.value = value
        self.tablename = tablename

    def __str__(self, level=0):
        out_string = "\t" * level + self.value + "\n"
        for child in self.children.values():
            out_string += child.__str__(level + 1)
        return out_string


# class that represents a select in the logical plan tree
class SelectNode(Node):
    # predicate: string type that will represent expression tree e.g. "v1.1 == 7"
    def __init__(self, predicate=''):
        super(SelectNode, self).__init__()
        self.predicate = predicate
        self.value = 'sigma {}'.format(self.predicate)


# class that represents projection in the logical plan tree
class ProjectionNode(Node):
    # columns: List of columns in a table that we want to project
    def __init__(self, columns=[]):
        super(ProjectionNode, self).__init__()
        self.columns = columns
        self.value ='pi {}'.format(','.join(self.columns))


# class that represents a natural join in the logical plan tree
class JoinNode(Node):
    # join_attrs: List of columns in a table that are the join variables
    # tables: List of string objects that represent the tables that are being joined
    def __init__(self, tables=[], join_attrs=[]):
        super(JoinNode, self).__init__()
        self.columns = tables
        self.join_attrs = join_attrs
        pt1 = ' join '.join(tables)
        pt2 = ' = '.join(join_attrs)
        self.tablename = '_'.join(tables)
        self.value = '{}__{}'.format(pt1, pt2)


# Class that represents the logical plan tree
class LogicalPlanTree():
    def __init__(self):
        self.root = None

    def __str__(self, level=0):
        return str(self.root)

# Class that encapsulates the functionality of the Rule Based Query Optimizer
class RuleQueryOptimizer():
    # Runs the query optimization
    def run(self, plan_tree):
        curnode = plan_tree.root
        self.traverse(curnode)
        return plan_tree

    # Traverses the tree recursively starting at the current node (curnode)
    # curnode is a Node type
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
    # curnode is a Node type
    # child is a Node type
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
    # TODO
    def simply_predicate(self, pred):
        new_pred = pred
        return new_pred

    # TODO
    def join_elimination(self, plan_tree):
        pass


# Function that test Predicate Pushdown on Hard Coded Tree
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


# Function that test Projection Pushdown on Hard Coded Tree
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
