from typing import List

from src.storage.abstract_loader import AbstractVideoLoader
from src.query_planner.abstract_inner_join_plan import AbstractInnerJoin
from src.query_planner.abstract_plan import PlanNodeType


class LogicalInnerJoinPlan(AbstractInnerJoin):
    """Class implementation for an inner join based planner
        Arguments:
            videos : list of videos on which the join will be executed
            join_id : columns that will be joined on in
            the form of "tablename.attribute"
        """

    def __init__(self, videos: List[AbstractVideoLoader], join_ids: List[str]):
        super().__init__(videos, join_ids)

    def get_node_type(self):
        return PlanNodeType.LOGICAL_INNER_JOIN

    # ToDo Add other functionality based on optimiser
