"""Abstract class for all the scan planners
https://www.postgresql.org/docs/9.1/using-explain.html
https://www.postgresql.org/docs/9.5/runtime-config-query.html
"""
from src.query_planner.abstract_plan import AbstractPlan
from src.loaders.abstract_loader import AbstractVideoLoader
from typing import List


class AbstractProjection(AbstractPlan):
    """Abstract class for all the projection based planners

    Arguments:
        predicate : Expression
        videos : list of videos on which the projection will be executed
        columns_id : columns in the form of "tablename.attribute"

    """

    def __init__(self, videos: List[AbstractVideoLoader], column_ids: List[str]):
        super(AbstractProjection, self).__init__()
        self._column_ids = column_ids
        self._videos = videos

    @property
    def videos(self) -> List[AbstractVideoLoader]:
        return self._videos

    @property
    def column_ids(self) -> List[str]:
        return self._column_ids

    def __str__(self, level=0):
        res = 'pi {}'.format(str(self._column_ids))
        ret = "\t" * level + res + "\n"
        for child in self.children:
            ret += child.__str__(level + 1)
        return ret