from typing import List

from src.loaders.abstract_loader import AbstractVideoLoader
from src.query_planner.abstract_inner_join_plan import AbstractInnerJoin
from src.query_planner.abstract_plan import PlanNodeType


class LogicalInnerJoinPlan(AbstractInnerJoin):
    def __init__(self, video1: AbstractVideoLoader, video2: AbstractVideoLoader,
                 join_ids: List[int]):
        super().__init__(video1, video2, join_ids)

    def get_node_type(self):
        return PlanNodeType.LOGICAL_INNER_JOIN

    # ToDo Add other functionality based on optimiser
