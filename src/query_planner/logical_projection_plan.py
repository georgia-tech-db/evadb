from typing import List

from src.loaders.abstract_loader import AbstractVideoLoader
from src.query_planner.abstract_projection_plan import AbstractProjection
from src.query_planner.abstract_plan import PlanNodeType


class LogicalProjectionPlan(AbstractProjection):
    """ Class for a Projection based planner

        Arguments:
            predicate : Expression
            videos : list of videos on which the projection will be executed
            columns_id : columns in the form of "tablename.attribute"

        """
    def __init__(self, videos: List[AbstractVideoLoader],
                 column_ids: List[str]):
        super().__init__(videos, column_ids)

    def get_node_type(self):
        return PlanNodeType.LOGICAL_PROJECTION

    # ToDo Add other functionality based on optimiser
