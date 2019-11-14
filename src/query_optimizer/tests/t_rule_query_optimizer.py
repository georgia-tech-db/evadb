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
from src.models import VideoMetaInfo, VideoFormat


def test_predicate_pushdown():
    print('Testing Predicate Pushdown')

    # Creating the videos
    meta1 = VideoMetaInfo(file='v1', c_format=VideoFormat.MOV, fps=30)
    video1 = SimpleVideoLoader(video_metadata=meta1)

    meta2 = VideoMetaInfo(file='v2', c_format=VideoFormat.MOV, fps=30)
    video2 = SimpleVideoLoader(video_metadata=meta2)

    projection_output = ['v1.1', 'v2.2']
    root = LogicalProjectionPlan(videos=[video1, video2], column_ids=projection_output)

    # Creating Expression for Select: Expression is basically where v1.1 == 4
    const = ConstantValueExpression(value=4)
    tup = TupleValueExpression(col_idx=int(projection_output[0].split('.')[1]))
    expression = ComparisonExpression(exp_type=ExpressionType.COMPARE_EQUAL, left=tup, right=const)

    # used both videos because purposely placed BEFORE the join
    s1 = LogicalSelectPlan(predicate=expression, column_ids=['v1.1'], videos=[video1, video2])
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
    print('Original Plan Tree')
    print(root)
    qo = RuleQueryOptimizer()
    new_tree = qo.run(root, rule_list)
    print('New Plan Tree')
    print(new_tree)


if __name__ == '__main__':
    test_predicate_pushdown()
