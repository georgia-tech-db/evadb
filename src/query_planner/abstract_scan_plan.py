"""Abstract class for all the scan planners
https://www.postgresql.org/docs/9.1/using-explain.html
https://www.postgresql.org/docs/9.5/runtime-config-query.html
"""
from src.expression.abstract_expression import AbstractExpression
from src.query_planner.abstract_plan import AbstractPlan
from src.loaders.abstract_loader import AbstractVideoLoader
from src.expression.abstract_expression import AbstractExpression
from typing import List
from src.query_planner.types import PlanNodeType


class AbstractScan(AbstractPlan):
    """Abstract class for all the scan based planners
    
    Arguments:
        predicate (AbstractExpression): An expression used for filtering
    """
    def __init__(self, predicate: AbstractExpression, video: AbstractVideoLoader,
                 column_ids: List[int]):
        super(AbstractScan, self).__init__()
        self._predicate = predicate
        self._column_ids = column_ids
        self._video = video

    @property
    def video(self) -> AbstractVideoLoader:
        return self._video

    @property
    def predicate(self) -> AbstractExpression:
        return self._predicate
