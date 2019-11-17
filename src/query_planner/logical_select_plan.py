from typing import List

from src.expression.abstract_expression import AbstractExpression
from src.loaders.abstract_loader import AbstractVideoLoader
from src.query_planner.abstract_select_plan import AbstractSelect
from src.query_planner.abstract_plan import PlanNodeType


class LogicalSelectPlan(AbstractSelect):
    """class for a select based planner

     Arguments:
         predicate : Expression
         videos : list of videos on which the select will be executed
         columns_id : columns used in the select in the form of "tablename.attribute"

     """
    def __init__(self, predicate: AbstractExpression,
                 videos: List[AbstractVideoLoader],
                 column_ids: List[str], foreign_column_ids: List[str]):
        super().__init__(predicate, videos, column_ids, foreign_column_ids)

    def get_node_type(self):
        return PlanNodeType.LOGICAL_SELECT

    # ToDo Add other functionality based on optimiser
