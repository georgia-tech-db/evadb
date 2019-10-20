# this is an implementation of a Rule Based Query Optimizer
import constants

query_list_test = ["c=white && t!=suv && t!=van"]

# list of filters available
synthetic_pp_list = ["t=suv", "t=van", "t=sedan", "t=truck",
                     "c=red", "c=white", "c=black", "c=silver",
                     "s>40", "s>50", "s>60", "s<65", "s<70",
                     "i=pt335", "i=pt211", "i=pt342", "i=pt208",
                     "o=pt335", "o=pt211", "o=pt342", "o=pt208"]

label_desc = {"t": [constants.DISCRETE, ["sedan", "suv", "truck", "van"]],
              "s": [constants.CONTINUOUS, [40, 50, 60, 65, 70]],
              "c": [constants.DISCRETE,
                    ["white", "red", "black", "silver"]],
              "i": [constants.DISCRETE,
                    ["pt335", "pt342", "pt211", "pt208"]],
              "o": [constants.DISCRETE,
                    ["pt335", "pt342", "pt211", "pt208"]]}

synthetic_pp_stats = {"t=van": {"none/dnn": {"R": 0.1, "C": 0.1, "A": 0.9},
                                "pca/dnn": {"R": 0.2, "C": 0.15,
                                            "A": 0.92},
                                "none/kde": {"R": 0.15, "C": 0.05,
                                             "A": 0.95}},
                      "t=suv": {
                          "none/svm": {"R": 0.13, "C": 0.01, "A": 0.95}},
                      "t=sedan": {
                          "none/svm": {"R": 0.21, "C": 0.01, "A": 0.94}},
                      "t=truck": {
                          "none/svm": {"R": 0.05, "C": 0.01, "A": 0.99}},

                      "c=red": {
                          "none/svm": {"R": 0.131, "C": 0.011,
                                       "A": 0.951}},
                      "c=white": {
                          "none/svm": {"R": 0.212, "C": 0.012,
                                       "A": 0.942}},
                      "c=black": {
                          "none/svm": {"R": 0.133, "C": 0.013,
                                       "A": 0.953}},
                      "c=silver": {
                          "none/svm": {"R": 0.214, "C": 0.014,
                                       "A": 0.944}},

                      "s>40": {
                          "none/svm": {"R": 0.08, "C": 0.20, "A": 0.8}},
                      "s>50": {
                          "none/svm": {"R": 0.10, "C": 0.20, "A": 0.82}},

                      "s>60": {
                          "none/dnn": {"R": 0.12, "C": 0.21, "A": 0.87},
                          "none/kde": {"R": 0.15, "C": 0.06, "A": 0.96}},

                      "s<65": {
                          "none/svm": {"R": 0.05, "C": 0.20, "A": 0.8}},
                      "s<70": {
                          "none/svm": {"R": 0.02, "C": 0.20, "A": 0.9}},

                      "o=pt211": {
                          "none/dnn": {"R": 0.135, "C": 0.324, "A": 0.993},
                          "none/kde": {"R": 0.143, "C": 0.123,
                                       "A": 0.932}},

                      "o=pt335": {
                          "none/dnn": {"R": 0.134, "C": 0.324, "A": 0.994},
                          "none/kde": {"R": 0.144, "C": 0.124,
                                       "A": 0.934}},

                      "o=pt342": {
                          "none/dnn": {"R": 0.135, "C": 0.325, "A": 0.995},
                          "none/kde": {"R": 0.145, "C": 0.125,
                                       "A": 0.935}},

                      "o=pt208": {
                          "none/dnn": {"R": 0.136, "C": 0.326, "A": 0.996},
                          "none/kde": {"R": 0.146, "C": 0.126,
                                       "A": 0.936}},

                      "i=pt211": {
                          "none/dnn": {"R": 0.135, "C": 0.324, "A": 0.993},
                          "none/kde": {"R": 0.143, "C": 0.123,
                                       "A": 0.932}},

                      "i=pt335": {
                          "none/dnn": {"R": 0.134, "C": 0.324, "A": 0.994},
                          "none/kde": {"R": 0.144, "C": 0.124,
                                       "A": 0.934}},

                      "i=pt342": {
                          "none/dnn": {"R": 0.135, "C": 0.325, "A": 0.995},
                          "none/kde": {"R": 0.145, "C": 0.125,
                                       "A": 0.935}},

                      "i=pt208": {
                          "none/dnn": {"R": 0.136, "C": 0.326, "A": 0.996},
                          "none/kde": {"R": 0.146, "C": 0.126,
                                       "A": 0.936}}}

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
    def __init__(self, filters, filter_stats, labels):
        self.filters = filters
        self.filter_stats = filter_stats
        self.labels = labels

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
    return plan_tree


def test_projection_push():
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
    return plan_tree




if __name__ == '__main__':
    #plan_tree = test_predicate_push()
    plan_tree = test_projection_push()
    print(plan_tree)
    qo = RuleQueryOptimizer(synthetic_pp_list, synthetic_pp_stats, label_desc)
    new_tree = qo.run(plan_tree)
    print(new_tree)
    # for query in query_list:
    #     print(query, " -> ", (
    #         qo.run(query)))