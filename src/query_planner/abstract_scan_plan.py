"""Abstract class for all the scan planners
https://www.postgresql.org/docs/9.1/using-explain.html
https://www.postgresql.org/docs/9.5/runtime-config-query.html
"""
from src.query_planner.abstract_plan import AbstractPlan
from typing import List


class AbstractScan(AbstractPlan):
    """Abstract class for all the scan based planners
    
    Arguments:
        predicate : Expression 
        video : video on which the scan will be executed
        columns_id :  

    """

    def __init__(self, predicate: Expression, video: Storage,
                 column_ids: List[int]):
        super(AbstractScan, self).__init__()
        self._predicate = predicate
        self._column_ids = column_ids
        self._video = video

    @property
    def video(self) -> Storage:
        return self._video

    @property
    def predicate(self) -> Expression:
        return self._predicate

    @property
    def column_ids(self) -> List:
        return self._column_ids
