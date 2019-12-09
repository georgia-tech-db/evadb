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
        predicate : Expression
        videos : list of videos on which the select will be executed
        columns_id : columns used in the select in the form of "tablename.attribute"
        foreign_column_id: columns in the form of "tablename.attribute"
    """
    def __init__(self, predicate: AbstractExpression, videos: List[AbstractVideoLoader],
                 column_ids: List[str], foreign_column_ids: List[str]):
        super(AbstractScan, self).__init__(PlanNodeType.SEQUENTIAL_SCAN_TYPE)
        self._predicate = predicate
        self._column_ids = column_ids
        self._videos = videos
        self._foreign_column_ids = foreign_column_ids

    @property
    def videos(self) -> List[AbstractVideoLoader]:
        """Returns the videos of the current node"""
        return self._videos

    @property
    def predicate(self) -> AbstractExpression:
        """Returns the predicate of the current node"""
        return self._predicate

    @property
    def column_ids(self) -> List[str]:
        """Returns the column ids of the current node"""
        return self._column_ids

    @property
    def foreign_column_ids(self) -> List[str]:
        """Returns the foreign key constraints of the current node"""
        return self._foreign_column_ids

    def set_videos(self, new_vids):
        """Sets the videos for the current node"""
        self._videos = new_vids

    def set_predicate(self, new_pred):
        """Sets the predicate for the current node"""
        self._predicate = new_pred

    def set_foreign_column_ids(self, foreign):
        """Sets the foreign key constraints of the current node"""
        self._foreign_column_ids = foreign

    def __str__(self, level=0):
        """Returns the representation of the node in string format"""
        select_cols_str = 'sigma {} {}'.format(str(self._predicate), str(self._foreign_column_ids))
        out_string = "\t" * level + select_cols_str + "\n"
        for child in self.children:
            out_string += child.__str__(level + 1)
        return out_string
