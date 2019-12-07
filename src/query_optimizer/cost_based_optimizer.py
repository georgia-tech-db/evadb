"""Cost based Optimizer for Eva"""

import logging
import src.constants as constants
from src.expression.abstract_expression import ExpressionType
from src.expression.comparison_expression import ComparisonExpression
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.tuple_value_expression import TupleValueExpression
from src.models.catalog.properties import VideoFormat
from src.models.catalog.video_info import VideoMetaInfo
from src.query_optimizer.pp_optimizer import PPOptimizer
from src.catalog.catalog import Catalog
from src.query_planner.abstract_plan import AbstractPlan
from src.query_planner.logical_inner_join_plan import LogicalInnerJoinPlan
from src.query_planner.logical_projection_plan import LogicalProjectionPlan
from src.query_planner.logical_select_plan import LogicalSelectPlan
from src.query_planner.video_table_plan import VideoTablePlan
from src.storage.video_loader import SimpleVideoLoader


class CostBasedOptimizer:

    def __init__(self, dataset: str):
        self._catalog = Catalog(dataset)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def execute(self,  node: AbstractPlan):
        pp_optimizer = PPOptimizer(self._catalog)
        for ind, child in enumerate(node.children):
            if type(child) == LogicalSelectPlan or type(child) == LogicalProjectionPlan:
                if child.predicate:
                    optimized_predicate, cost = pp_optimizer.execute(child.predicate)
                    self.logger.info("Optimized predicate from "+str(child.predicate) +
                                     " to "+ str(optimized_predicate) + " with cost " +str(cost))
                    child.set_predicate(optimized_predicate)
                    self.execute(child)


if __name__ == '__main__':
    meta1 = VideoMetaInfo(file='v1', c_format=VideoFormat.MOV, fps=30)
    video1 = SimpleVideoLoader(video_metadata=meta1)

    meta2 = VideoMetaInfo(file='v2', c_format=VideoFormat.MOV, fps=30)
    video2 = SimpleVideoLoader(video_metadata=meta2)

    projection_output = ['v1.1', 'v2.2']
    root = LogicalProjectionPlan(videos=[video1, video2], column_ids=projection_output, foreign_column_ids=[])

    # Creating Expression for Select: Expression is basically where v1.1 == 4
    const = ConstantValueExpression(value=4)
    tup = TupleValueExpression(col_idx=int(projection_output[0].split('.')[1]))
    tup.set_col_name("1")

    expression = ComparisonExpression(exp_type=ExpressionType.COMPARE_EQUAL, left=tup, right=const)

    # used both videos because purposely placed BEFORE the join
    s1 = LogicalSelectPlan(predicate=expression, column_ids=['v1.1'], videos=[video1, video2], foreign_column_ids=[])
    s1.parent = root

    j1 = LogicalInnerJoinPlan(videos=[video1, video2], join_ids=['v1.3', 'v2.3'])
    j1.parent = s1

    t1 = VideoTablePlan(video=video1, tablename='v1')
    t2 = VideoTablePlan(video=video2, tablename='v2')

    # s1.set_children([j1])
    s1.append_child(j1)
    t1.parent = j1
    t2.parent = j1

    # j1.set_children([t1, t2])
    j1.append_child(t1)
    j1.append_child(t2)
    # root.set_children([s1])
    root.append_child(s1)

    cb_optimzer = CostBasedOptimizer(constants.UADETRAC)
    cb_optimzer.execute(root)