"""Abstract class for all the scan planners
https://www.postgresql.org/docs/9.1/using-explain.html
https://www.postgresql.org/docs/9.5/runtime-config-query.html
"""
from src.query_planner.abstract_plan import AbstractPlan
from src.loaders.abstract_loader import AbstractVideoLoader
from typing import List


class AbstractProjection(AbstractPlan):
    """Abstract class for all the scan based planners

    Arguments:
        predicate : Expression
        video : video on which the scan will be executed
        columns_id :

    """

    def __init__(self, video: AbstractVideoLoader, column_ids: List[int]):
        super(AbstractProjection, self).__init__()
        self._column_ids = column_ids
        self._video = video

    @property
    def video(self) -> AbstractVideoLoader:
        return self._video

    @property
    def column_ids(self) -> List:
        return self._column_ids
