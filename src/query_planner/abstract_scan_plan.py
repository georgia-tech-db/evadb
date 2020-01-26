"""Abstract class for all the scan planners
https://www.postgresql.org/docs/9.1/using-explain.html
https://www.postgresql.org/docs/9.5/runtime-config-query.html
"""
from src.expression.abstract_expression import AbstractExpression
from src.query_planner.abstract_plan import AbstractPlan

from src.query_planner.types import PlanNodeType
from src.query_parser.table_ref import TableRef
from typing import List


class AbstractScan(AbstractPlan):
    """Abstract class for all the scan based planners
    
    Arguments:
        column_ids: List[str] 
            list of column names string in the plan
        video: TableRef
            video reference for the plan
        predicate: AbstractExpression
            An expression used for filtering
    """

    def __init__(self, node_type: PlanNodeType, column_ids: List[AbstractExpression], video: TableRef, predicate: AbstractExpression):
        super(AbstractPlan, self).__init__(node_type)
        self._column_ids = column_ids
        self._video = video
        self._predicate = predicate

    @property
    def predicate(self) -> AbstractExpression:
        return self._predicate

    @property
    def column_ids(self) -> List[AbstractExpression]:
        return self._column_ids
    
    @property
    def video(self) -> TableRef:
        return self._video
        