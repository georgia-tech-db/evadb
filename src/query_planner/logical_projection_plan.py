from typing import List

from src.loaders.abstract_loader import AbstractVideoLoader
from src.query_planner.abstract_projection_plan import AbstractProjection
from src.query_planner.abstract_plan import PlanNodeType


class LogicalProjectionPlan(AbstractProjection):
    def __init__(self, video: AbstractVideoLoader,
                 column_ids: List[int]):
        super().__init__(video, column_ids)

    def get_node_type(self):
        return PlanNodeType.LOGICAL_PROJECTION

    # ToDo Add other functionality based on optimiser
