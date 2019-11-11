"""Abstract class for all the scan planners
https://www.postgresql.org/docs/9.1/using-explain.html
https://www.postgresql.org/docs/9.5/runtime-config-query.html
"""
from src.query_planner.abstract_plan import AbstractPlan
from src.loaders.abstract_loader import AbstractVideoLoader
from typing import List


class AbstractInnerJoin(AbstractPlan):
    """Abstract class for all the scan based planners

    Arguments:
        predicate : Expression
        video : video on which the scan will be executed
        columns_id :

    """

    def __init__(self, video1: AbstractVideoLoader, video2: AbstractVideoLoader, join_ids: List[int]):
        super(AbstractInnerJoin, self).__init__()
        self._join_ids = join_ids
        self._video1 = video1
        self._video2 = video2

    @property
    def video(self) -> List:
        return [self._video1, self._video2]

    @property
    def join_ids(self) -> List:
        return self._join_ids
