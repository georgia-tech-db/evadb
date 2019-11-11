from typing import List

from src.expression.abstract_expression import AbstractExpression
from src.loaders.abstract_loader import AbstractVideoLoader
from src.query_planner.abstract_select_plan import AbstractSelect
from src.query_planner.abstract_plan import PlanNodeType


class LogicalSelectPlan(AbstractSelect):
    def __init__(self, predicate: AbstractExpression,
                 video: AbstractVideoLoader,
                 column_ids: List[int]):
        super().__init__(predicate, video, column_ids)

    def get_node_type(self):
        return PlanNodeType.LOGICAL_SELECT

    # ToDo Add other functionality based on optimiser
