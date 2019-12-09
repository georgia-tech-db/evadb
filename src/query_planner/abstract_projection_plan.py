"""Abstract class for all the scan planners
https://www.postgresql.org/docs/9.1/using-explain.html
https://www.postgresql.org/docs/9.5/runtime-config-query.html
"""
from src.query_planner.abstract_plan import AbstractPlan
from src.loaders.abstract_loader import AbstractVideoLoader
from typing import List
from src.query_planner.abstract_plan import PlanNodeType


class AbstractProjection(AbstractPlan):
    """Abstract class for all the projection based planners

    Arguments:
        predicate : Expression
        videos : list of videos on which the projection will be executed
        columns_id : columns in the form of "tablename.attribute"
        foreign_column_id: columns in the form of "tablename.attribute"

    """

    def __init__(self, videos: List[AbstractVideoLoader], column_ids: List[str], foreign_column_ids: List[str]):
        super(AbstractProjection, self).__init__(PlanNodeType.LOGICAL_PROJECTION)
        self._column_ids = column_ids
        self._videos = videos
        self._foreign_column_ids = foreign_column_ids

    @property
    def videos(self) -> List[AbstractVideoLoader]:
        return self._videos

    @property
    def column_ids(self) -> List[str]:
        return self._column_ids

    @property
    def foreign_column_ids(self) -> List[str]:
        return self._foreign_column_ids

    def set_foreign_column_ids(self, foreign):
        self._foreign_column_ids = foreign

    def set_column_ids(self, new_id):
        self._column_ids = new_id

    def __str__(self, level=0):
        project_cols_str = 'pi {} {}'.format(str(self._column_ids), str(self._foreign_column_ids))
        out_string = "\t" * level + project_cols_str + "\n"
        for child in self.children:
            out_string += child.__str__(level + 1)
        return out_string