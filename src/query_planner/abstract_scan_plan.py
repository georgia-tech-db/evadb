"""Abstract class for all the scan planners
https://www.postgresql.org/docs/9.1/using-explain.html
https://www.postgresql.org/docs/9.5/runtime-config-query.html
"""
from src.query_planner.abstract_plan import AbstractPlan
from typing import List

from src.query_planner.types import PlanNodeType


class AbstractScan(AbstractPlan):
    """Abstract class for all the scan based planners
    
    Arguments:
        predicate : Expression 
        columns_id :
    """

    def __init__(self, node_type: PlanNodeType, predicate: 'Expression',
                 column_ids: List[int]):
        super(AbstractScan, self).__init__(node_type)
        self._predicate = predicate
        self._column_ids = column_ids

    @property
    def predicate(self) -> 'Expression':
        return self._predicate

    @property
    def column_ids(self) -> List:
        return self._column_ids
