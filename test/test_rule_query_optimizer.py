import unittest
from query_optimizer.rule_query_optimizer import RuleQueryOptimizer, Rules
from expression.comparison_expression import ComparisonExpression
from expression.abstract_expression import ExpressionType
from expression.constant_value_expression import ConstantValueExpression
from expression.tuple_value_expression import TupleValueExpression
from query_planner.logical_select_plan import LogicalSelectPlan
from query_planner.logical_inner_join_plan import LogicalInnerJoinPlan
from query_planner.logical_projection_plan import LogicalProjectionPlan
from query_planner.video_table_plan import VideoTablePlan
from loaders.video_loader import SimpleVideoLoader
#from models import VideoFormat, VideoMetaInfo
from models.catalog.video_info import VideoMetaInfo
from models.catalog.properties import VideoFormat

class RuleQueryOptimizerTest(unittest.TestCase):

    def test_simple_predicate_pushdown(self, verbose=False):
        # Creating the videos
        meta1 = VideoMetaInfo(file='v1', c_format=VideoFormat.MOV, fps=30)
        video1 = SimpleVideoLoader(video_metadata=meta1)

        meta2 = VideoMetaInfo(file='v2', c_format=VideoFormat.MOV, fps=30)
        video2 = SimpleVideoLoader(video_metadata=meta2)

        projection_output = ['v1.1', 'v2.2']
        root = LogicalProjectionPlan(videos=[video1, video2], column_ids=projection_output, foreign_column_ids=[])

        # Creating Expression for Select: Expression is basically where v1.1 == 4
        const = ConstantValueExpression(value=4)
        tup = TupleValueExpression(col_idx=int(projection_output[0].split('.')[1]))
        expression = ComparisonExpression(exp_type=ExpressionType.COMPARE_EQUAL, left=tup, right=const)

        # used both videos because purposely placed BEFORE the join
        s1 = LogicalSelectPlan(predicate=expression, column_ids=['v1.1'], videos=[video1, video2],
                               foreign_column_ids=[])
        s1.parent = root

        j1 = LogicalInnerJoinPlan(videos=[video1, video2], join_ids=['v1.3', 'v2.3'])
        j1.parent = s1

        t1 = VideoTablePlan(video=video1, tablename='v1')
        t2 = VideoTablePlan(video=video2, tablename='v2')

        s1.set_children([j1])
        t1.parent = j1
        t2.parent = j1

        j1.set_children([t1, t2])
        root.set_children([s1])

        rule_list = [Rules.PREDICATE_PUSHDOWN]
        if verbose:
            print('Original Plan Tree')
            print(root)
        qo = RuleQueryOptimizer()
        new_tree = qo.run(root, rule_list)
        if verbose:
            print('New Plan Tree')
            print(new_tree)

        self.assertIsNone(root.parent, None)
        self.assertEqual(root.children, [j1])
        self.assertEqual(j1.parent, root)
        self.assertEqual(j1.children, [s1, t2])
        self.assertEqual(s1.parent, j1)
        self.assertEqual(s1.videos, [video1])
        self.assertEqual(t2.parent, j1)
        self.assertEqual(s1.children, [t1])
        self.assertEqual(t1.parent, s1)

    def test_simple_projection_pushdown_join(self, verbose=False):
        # Creating the videos
        meta1 = VideoMetaInfo(file='v1', c_format=VideoFormat.MOV, fps=30)
        video1 = SimpleVideoLoader(video_metadata=meta1)

        meta2 = VideoMetaInfo(file='v2', c_format=VideoFormat.MOV, fps=30)
        video2 = SimpleVideoLoader(video_metadata=meta2)

        projection_output = ['v1.3', 'v2.4']
        root = LogicalProjectionPlan(videos=[video1, video2], column_ids=projection_output, foreign_column_ids=[])

        j1 = LogicalInnerJoinPlan(videos=[video1, video2], join_ids=['v1.1', 'v2.1'])
        j1.parent = root

        t1 = VideoTablePlan(video=video1, tablename='v1')
        t2 = VideoTablePlan(video=video2, tablename='v2')

        t1.parent = j1
        t2.parent = j1

        j1.set_children([t1, t2])
        root.set_children([j1])

        rule_list = [Rules.PROJECTION_PUSHDOWN_JOIN]
        if verbose:
            print('Original Plan Tree')
            print(root)
        qo = RuleQueryOptimizer()
        new_tree = qo.run(root, rule_list)
        if verbose:
            print('New Plan Tree')
            print(new_tree)

        self.assertIsNone(root.parent)
        self.assertEqual(root.children, [j1])
        self.assertEqual(j1.parent, root)
        self.assertEqual(type(j1.children[0]), LogicalProjectionPlan)
        self.assertEqual(type(j1.children[1]), LogicalProjectionPlan)
        self.assertTrue('v1.1' in j1.children[0].column_ids)
        self.assertTrue('v1.3' in j1.children[0].column_ids)
        self.assertTrue('v2.1' in j1.children[1].column_ids)
        self.assertTrue('v2.4' in j1.children[1].column_ids)
        self.assertEqual(type(t2.parent), LogicalProjectionPlan)
        self.assertEqual(type(t1.parent), LogicalProjectionPlan)
        self.assertEqual(j1.children[0].children, [t1])
        self.assertEqual(j1.children[1].children, [t2])

    def test_simple_projection_pushdown_select(self, verbose=False):
        meta1 = VideoMetaInfo(file='v1', c_format=VideoFormat.MOV, fps=30)
        video1 = SimpleVideoLoader(video_metadata=meta1)

        # Creating Expression for Select: Expression is basically where v2.7 == 4
        const = ConstantValueExpression(value=4)
        tup = TupleValueExpression(col_idx=int(7))
        expression = ComparisonExpression(exp_type=ExpressionType.COMPARE_EQUAL, left=tup, right=const)
        s1 = LogicalSelectPlan(predicate=expression, column_ids=['v1.7'], videos=[video1], foreign_column_ids=[])

        projection_output = ['v1.3', 'v1.4']
        root = LogicalProjectionPlan(videos=[video1], column_ids=projection_output, foreign_column_ids=[])

        t1 = VideoTablePlan(video=video1, tablename='v1')

        root.set_children([s1])
        s1.parent = root
        s1.set_children([t1])
        t1.parent = s1

        rule_list = [Rules.PROJECTION_PUSHDOWN_SELECT]
        if verbose:
            print('Original Plan Tree')
            print(root)
        qo = RuleQueryOptimizer()
        new_tree = qo.run(root, rule_list)
        if verbose:
            print('New Plan Tree')
            print(new_tree)

        self.assertIsNone(root.parent)
        self.assertEqual(root.children, [s1])
        self.assertEqual(s1.parent, root)
        self.assertEqual(len(s1.children), 1)
        self.assertEqual(type(s1.children[0]), LogicalProjectionPlan)
        self.assertTrue('v1.7' in s1.children[0].column_ids)
        self.assertTrue('v1.3' in s1.children[0].column_ids)
        self.assertTrue('v1.4' in s1.children[0].column_ids)
        self.assertEqual(type(t1.parent) , LogicalProjectionPlan)
        self.assertEqual(s1.children[0].children, [t1])

    def test_combined_projection_pushdown(self, verbose=False):
        # Creating the videos
        meta1 = VideoMetaInfo(file='v1', c_format=VideoFormat.MOV, fps=30)
        video1 = SimpleVideoLoader(video_metadata=meta1)

        meta2 = VideoMetaInfo(file='v2', c_format=VideoFormat.MOV, fps=30)
        video2 = SimpleVideoLoader(video_metadata=meta2)

        projection_output = ['v1.3', 'v2.4']
        root = LogicalProjectionPlan(videos=[video1, video2], column_ids=projection_output, foreign_column_ids=[])

        j1 = LogicalInnerJoinPlan(videos=[video1, video2], join_ids=['v1.1', 'v2.1'])
        j1.parent = root

        const = ConstantValueExpression(value=4)
        tup = TupleValueExpression(col_idx=int(7))
        expression = ComparisonExpression(exp_type=ExpressionType.COMPARE_EQUAL, left=tup, right=const)
        s1 = LogicalSelectPlan(predicate=expression, column_ids=['v2.7'], videos=[video1], foreign_column_ids=[])
        s1.parent = j1

        t1 = VideoTablePlan(video=video1, tablename='v1')
        t2 = VideoTablePlan(video=video2, tablename='v2')
        s1.set_children([t2])
        t1.parent = j1
        t2.parent = s1

        j1.set_children([t1, s1])
        root.set_children([j1])

        rule_list = [Rules.PROJECTION_PUSHDOWN_JOIN, Rules.PROJECTION_PUSHDOWN_SELECT]
        if verbose:
            print('Original Plan Tree')
            print(root)
        qo = RuleQueryOptimizer()
        new_tree = qo.run(root, rule_list)
        if verbose:
            print('New Plan Tree')
            print(new_tree)

        self.assertIsNone(root.parent)
        self.assertEqual(root.children, [j1])
        self.assertEqual(j1.parent, root)
        self.assertEqual(type(j1.children[0]), LogicalProjectionPlan)
        self.assertEqual(type(j1.children[1]), LogicalProjectionPlan)
        self.assertEqual(type(s1.parent), LogicalProjectionPlan)
        self.assertTrue('v2.1' in s1.parent.column_ids)
        self.assertTrue('v2.4' in s1.parent.column_ids)
        self.assertTrue(s1.parent in j1.children)
        self.assertEqual(len(s1.children) , 1)
        self.assertEqual(type(s1.children[0]), LogicalProjectionPlan)
        self.assertTrue('v2.7' in s1.children[0].column_ids)
        self.assertTrue('v2.1' in s1.children[0].column_ids)
        self.assertTrue('v2.4' in s1.children[0].column_ids)
        self.assertEqual(type(t1.parent), LogicalProjectionPlan)
        self.assertTrue('v1.1' in t1.parent.column_ids)
        self.assertTrue('v1.3' in t1.parent.column_ids)
        self.assertTrue(t1.parent in j1.children)
        self.assertEqual(s1.children[0].children, [t2])

    def test_both_projection_pushdown_and_predicate_pushdown(self, verbose=False):
        meta1 = VideoMetaInfo(file='v1', c_format=VideoFormat.MOV, fps=30)
        video1 = SimpleVideoLoader(video_metadata=meta1)

        meta2 = VideoMetaInfo(file='v2', c_format=VideoFormat.MOV, fps=30)
        video2 = SimpleVideoLoader(video_metadata=meta2)

        projection_output = ['v1.1', 'v2.2']
        root = LogicalProjectionPlan(videos=[video1, video2], column_ids=projection_output, foreign_column_ids=[])

        # Creating Expression for Select: Expression is basically where v1.1 == 4
        const = ConstantValueExpression(value=4)
        tup = TupleValueExpression(col_idx=int(projection_output[0].split('.')[1]))
        expression = ComparisonExpression(exp_type=ExpressionType.COMPARE_EQUAL, left=tup, right=const)

        # used both videos because purposely placed BEFORE the join
        s1 = LogicalSelectPlan(predicate=expression, column_ids=['v1.1'], videos=[video1, video2],
                               foreign_column_ids=[])
        s1.parent = root

        j1 = LogicalInnerJoinPlan(videos=[video1, video2], join_ids=['v1.3', 'v2.3'])
        j1.parent = s1

        t1 = VideoTablePlan(video=video1, tablename='v1')
        t2 = VideoTablePlan(video=video2, tablename='v2')

        s1.set_children([j1])
        t1.parent = j1
        t2.parent = j1

        j1.set_children([t1, t2])
        root.set_children([s1])

        rule_list = [Rules.PREDICATE_PUSHDOWN, Rules.PROJECTION_PUSHDOWN_JOIN, Rules.PROJECTION_PUSHDOWN_SELECT]
        if verbose:
            print('Original Plan Tree')
            print(root)
        qo = RuleQueryOptimizer()
        new_tree = qo.run(root, rule_list)
        if verbose:
            print('New Plan Tree')
            print(new_tree)

        self.assertIsNone(root.parent)
        self.assertEqual(root.children, [j1])
        self.assertEqual(j1.parent, root)
        self.assertEqual(len(j1.children), 2)
        self.assertTrue(s1 in j1.children)
        self.assertEqual(s1.parent, j1)
        self.assertEqual(s1.videos, [video1])
        self.assertEqual(len(s1.children), 1)
        self.assertEqual(type(s1.children[0]), LogicalProjectionPlan)
        self.assertTrue('v1.1' in s1.children[0].column_ids)
        self.assertTrue('v1.3' in s1.children[0].column_ids)
        self.assertEqual(s1.children[0].children, [t1])
        self.assertEqual(t1.parent, s1.children[0])
        s1_ix = j1.children.index(s1)
        if s1_ix == 0:
            proj_ix = 1
        else:
            proj_ix = 0
        self.assertEqual(type(j1.children[proj_ix]), LogicalProjectionPlan)
        self.assertEqual(j1.children[proj_ix].parent, j1)
        self.assertTrue('v2.3' in j1.children[proj_ix].column_ids)
        self.assertTrue('v2.2' in j1.children[proj_ix].column_ids)
        self.assertEqual(t2.parent, j1.children[proj_ix])

    def test_double_join_predicate_pushdown(self, verbose=False):
        meta1 = VideoMetaInfo(file='v1', c_format=VideoFormat.MOV, fps=30)
        video1 = SimpleVideoLoader(video_metadata=meta1)

        meta2 = VideoMetaInfo(file='v2', c_format=VideoFormat.MOV, fps=30)
        video2 = SimpleVideoLoader(video_metadata=meta2)

        meta3 = VideoMetaInfo(file='v3', c_format=VideoFormat.MOV, fps=30)
        video3 = SimpleVideoLoader(video_metadata=meta3)

        projection_output = ['v1.1', 'v2.2', 'v3.4']
        root = LogicalProjectionPlan(videos=[video1, video2, video3], column_ids=projection_output,
                                     foreign_column_ids=[])

        # Creating Expression for Select: Expression is basically where v3.3 == 4
        const = ConstantValueExpression(value=4)
        tup = TupleValueExpression(col_idx=int(projection_output[2].split('.')[1]))
        expression = ComparisonExpression(exp_type=ExpressionType.COMPARE_EQUAL, left=tup, right=const)

        # used both videos because purposely placed BEFORE the join
        s1 = LogicalSelectPlan(predicate=expression, column_ids=['v3.3'], videos=[video1, video2, video3],
                               foreign_column_ids=[])
        s1.parent = root

        j1 = LogicalInnerJoinPlan(videos=[video1, video2], join_ids=['v1.3', 'v2.3'])
        j2 = LogicalInnerJoinPlan(videos=[video1, video2, video3], join_ids=['v1.3', 'v2.3', 'v3.3'])
        j1.parent = j2

        t1 = VideoTablePlan(video=video1, tablename='v1')
        t2 = VideoTablePlan(video=video2, tablename='v2')
        t3 = VideoTablePlan(video=video3, tablename='v3')

        s1.set_children([j2])
        t1.parent = j1
        t2.parent = j1
        j2.set_children([j1, t3])
        t3.parent = j2
        j1.set_children([t1, t2])
        root.set_children([s1])

        rule_list = [Rules.PREDICATE_PUSHDOWN]
        if verbose:
            print('Original Plan Tree')
            print(root)
        qo = RuleQueryOptimizer()
        new_tree = qo.run(root, rule_list)
        if verbose:
            print('New Plan Tree')
            print(new_tree)

        self.assertIsNone(root.parent)
        self.assertEqual(len(root.children), 1)
        self.assertEqual(root.children[0].parent, root)
        self.assertEqual(j2.parent, root)
        self.assertEqual(len(j2.children), 2)
        self.assertEqual(j2.children[0], j1)
        self.assertEqual(j2.children[1], s1)
        self.assertEqual(s1.parent, j2)
        self.assertEqual(j1.parent, j2)
        self.assertEqual(len(s1.videos), 1)
        self.assertEqual(s1.videos[0], video3)
        self.assertEqual(len(s1.children), 1)
        self.assertEqual(s1.children[0], t3)
        self.assertEqual(t3.parent, s1)
        self.assertEqual(len(j1.children), 2)
        self.assertEqual(j1.children[0], t1)
        self.assertEqual(j1.children[1], t2)
        self.assertEqual(t1.parent, j1)
        self.assertEqual(t2.parent, j1)

    def test_double_join_projection_pushdown(self, verbose=False):
        meta1 = VideoMetaInfo(file='v1', c_format=VideoFormat.MOV, fps=30)
        video1 = SimpleVideoLoader(video_metadata=meta1)

        meta2 = VideoMetaInfo(file='v2', c_format=VideoFormat.MOV, fps=30)
        video2 = SimpleVideoLoader(video_metadata=meta2)

        meta3 = VideoMetaInfo(file='v3', c_format=VideoFormat.MOV, fps=30)
        video3 = SimpleVideoLoader(video_metadata=meta3)

        projection_output = ['v1.1', 'v2.2', 'v3.4']
        root = LogicalProjectionPlan(videos=[video1, video2, video3], column_ids=projection_output,
                                     foreign_column_ids=[])

        j1 = LogicalInnerJoinPlan(videos=[video1, video2], join_ids=['v1.3', 'v2.3'])
        j2 = LogicalInnerJoinPlan(videos=[video1, video2, video3], join_ids=['v1.3', 'v2.3', 'v3.3'])
        j1.parent = j2
        j2.parent = root
        t1 = VideoTablePlan(video=video1, tablename='v1')
        t2 = VideoTablePlan(video=video2, tablename='v2')
        t3 = VideoTablePlan(video=video3, tablename='v3')

        t1.parent = j1
        t2.parent = j1
        j2.set_children([t3, j1])
        t3.parent = j2
        j1.set_children([t1, t2])
        root.set_children([j2])

        rule_list = [Rules.PROJECTION_PUSHDOWN_JOIN]
        if verbose:
            print('Original Plan Tree')
            print(root)
        qo = RuleQueryOptimizer()
        new_tree = qo.run(root, rule_list)
        if verbose:
            print('New Plan Tree')
            print(new_tree)

        self.assertIsNone(root.parent)
        self.assertTrue('v1.1' in root.column_ids)
        self.assertTrue('v2.2' in root.column_ids)
        self.assertTrue('v3.4' in root.column_ids)
        self.assertEqual(len(root.children), 1)
        self.assertEqual(root.children[0], j2)
        self.assertEqual(j2.parent, root)
        self.assertEqual(len(j2.videos), 3)
        self.assertTrue(video1 in j2.videos)
        self.assertTrue(video2 in j2.videos)
        self.assertTrue(video3 in j2.videos)
        self.assertEqual(len(j2.children), 2)
        self.assertTrue(j1 in j2.children)
        j1_ix = j2.children.index(j1)
        pix = 1 - j1_ix
        self.assertEqual(type(j2.children[pix]), LogicalProjectionPlan)
        self.assertEqual(len(j2.children[pix].column_ids), 2)
        self.assertTrue('v3.4' in j2.children[pix].column_ids)
        self.assertTrue('v3.3' in j2.children[pix].column_ids)
        self.assertEqual(j2.children[pix].parent, j2)
        self.assertEqual(len(j2.children[pix].children), 1)
        self.assertEqual(j2.children[pix].children[0], t3)
        self.assertEqual(len(j1.videos), 2)
        self.assertTrue(video1 in j1.videos)
        self.assertTrue(video2 in j1.videos)
        self.assertEqual(len(j1.children), 2)
        self.assertEqual(type(j1.children[0]), LogicalProjectionPlan)
        self.assertEqual(type(j1.children[1]), LogicalProjectionPlan)
        self.assertEqual(len(j1.children[0].column_ids), 2)
        self.assertEqual(len(j1.children[0].children), 1)
        self.assertEqual(j1.children[0].children[0], t1)
        self.assertEqual(len(j1.children[1].children), 1)
        self.assertEqual(j1.children[1].children[0], t2)
        self.assertTrue('v1.3' in j1.children[0].column_ids)
        self.assertTrue('v1.1' in j1.children[0].column_ids)
        self.assertEqual(len(j1.children[1].column_ids), 2)
        self.assertTrue('v2.3' in j1.children[1].column_ids)
        self.assertTrue('v2.2' in j1.children[1].column_ids)
        self.assertEqual(j1.children[0].parent, j1)
        self.assertEqual(j1.children[1].parent, j1)

    def test_should_simply_predicate(self,verbose=False):
        meta1 = VideoMetaInfo(file='v1', c_format=VideoFormat.MOV, fps=30)
        video1 = SimpleVideoLoader(video_metadata=meta1)

        # Creating Expression for Select: Expression is basically where 0==1
        const1 = ConstantValueExpression(value=0)
        const2 = ConstantValueExpression(value=1)
        expression = ComparisonExpression(exp_type=ExpressionType.COMPARE_EQUAL, left=const1, right=const2)
        s1 = LogicalSelectPlan(predicate=expression, column_ids=[], videos=[], foreign_column_ids=[])

        projection_output = ['v1.3', 'v1.4']
        root = LogicalProjectionPlan(videos=[video1], column_ids=projection_output, foreign_column_ids=[])

        t1 = VideoTablePlan(video=video1, tablename='v1')

        root.set_children([s1])
        s1.parent = root
        s1.set_children([t1])
        t1.parent = s1
        rule_list = [Rules.SIMPLIFY_PREDICATE]
        if verbose:
            print('Original Plan Tree')
            print(root)
        qo = RuleQueryOptimizer()
        new_tree = qo.run(root, rule_list)
        if verbose:
            print('New Plan Tree')
            print(new_tree)

        self.assertIsNone(root.parent)
        self.assertEqual(root.children, [t1])
        self.assertEqual(t1.parent, root)
        self.assertEqual(len(root.children), 1)
        self.assertTrue('v1.7' in root.children[0].column_ids)
        self.assertTrue('v1.3' in root.children[0].column_ids)
        self.assertTrue('v1.4' in root.children[0].column_ids)
        self.assertEqual(type(t1.parent) , LogicalProjectionPlan)
        self.assertEqual(root.children[0].children, [t1])

    def test_should_not_simply_predicate(self,verbose=False):
        meta1 = VideoMetaInfo(file='v1', c_format=VideoFormat.MOV, fps=30)
        video1 = SimpleVideoLoader(video_metadata=meta1)

        # Creating Expression for Select: Expression is basically where v1.7 == 4
        const = ConstantValueExpression(value=4)
        tup = TupleValueExpression(col_idx=int(7))
        expression = ComparisonExpression(exp_type=ExpressionType.COMPARE_EQUAL, left=tup, right=const)
        s1 = LogicalSelectPlan(predicate=expression, column_ids=[], videos=[], foreign_column_ids=[])

        projection_output = ['v1.3', 'v1.4']
        root = LogicalProjectionPlan(videos=[video1], column_ids=projection_output, foreign_column_ids=[])

        t1 = VideoTablePlan(video=video1, tablename='v1')

        root.set_children([s1])
        s1.parent = root
        s1.set_children([t1])
        t1.parent = s1
        rule_list = [Rules.SIMPLIFY_PREDICATE]
        if verbose:
            print('Original Plan Tree')
            print(root)
        qo = RuleQueryOptimizer()
        new_tree = qo.run(root, rule_list)
        if verbose:
            print('New Plan Tree')
            print(new_tree)

        self.assertIsNone(root.parent)
        self.assertEqual(root.children, [s1])
        self.assertEqual(s1.parent, root)
        self.assertEqual(len(s1.children), 1)
        self.assertEqual(type(s1.children[0]), LogicalProjectionPlan)
        self.assertTrue('v1.7' in s1.children[0].column_ids)
        self.assertTrue('v1.3' in s1.children[0].column_ids)
        self.assertTrue('v1.4' in s1.children[0].column_ids)
        self.assertEqual(type(t1.parent) , LogicalProjectionPlan)
        self.assertEqual(s1.children[0].children, [t1])

    def test_join_elimination(self, verbose=False):
        meta1 = VideoMetaInfo(file='v1', c_format=VideoFormat.MOV, fps=30)
        video1 = SimpleVideoLoader(video_metadata=meta1)

        meta2 = VideoMetaInfo(file='v2', c_format=VideoFormat.MOV, fps=30)
        video2 = SimpleVideoLoader(video_metadata=meta2)

        projection_output = ['v1.1', 'v2.2']
        root = LogicalProjectionPlan(videos=[video1, video2], column_ids=projection_output, foreign_column_ids=['v2.2'])

        # Creating Expression for Select: Expression is basically where v1.1 == v2.2
        # Also creating a foreign key constraint for v1 where it requires v2.2
        # hence join elimination should delete the join node and just return all of v1.1 for select
        tup1 = TupleValueExpression(col_idx=1)
        tup2 = TupleValueExpression(col_idx=2)
        expression = ComparisonExpression(exp_type=ExpressionType.COMPARE_EQUAL, left=tup1, right=tup2)

        # used both videos because purposely placed BEFORE the join
        s1 = LogicalSelectPlan(predicate=expression, column_ids=['v1.1', 'v2.2'], videos=[video1, video2],
                               foreign_column_ids=['v2.2'])
        s1.parent = root

        j1 = LogicalInnerJoinPlan(videos=[video1, video2], join_ids=['v1.1', 'v2.2'])
        j1.parent = s1

        t1 = VideoTablePlan(video=video1, tablename='v1')
        t2 = VideoTablePlan(video=video2, tablename='v2')
        t1.parent = j1
        t2.parent = j1

        root.set_children([s1])
        s1.set_children([j1])
        j1.set_children([t1, t2])

        rule_list = [Rules.JOIN_ELIMINATION]

        if verbose:
            print('Original Plan Tree')
            print(root)
        qo = RuleQueryOptimizer()
        new_tree = qo.run(root, rule_list)
        if verbose:
            print('New Plan Tree')
            print(new_tree)

        self.assertIsNone(root.parent)
        self.assertEqual(type(t1.parent), LogicalSelectPlan)
        self.assertEqual(type(s1.children[0]), VideoTablePlan)
        self.assertEqual(len(s1.children), 1)
        self.assertEqual(len(s1.foreign_column_ids), 0)
        self.assertTrue('v1.2' in root.column_ids)
        self.assertEqual(len(root.column_ids), 2)
        self.assertEqual(len(root.foreign_column_ids), 0)
        self.assertEqual(type(root.children[0]), LogicalSelectPlan)

