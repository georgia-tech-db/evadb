"""Abstract class for all the scan planners
https://www.postgresql.org/docs/9.1/using-explain.html
https://www.postgresql.org/docs/9.5/runtime-config-query.html
"""
from src.query_planner.abstract_plan import AbstractPlan
from src.expression.abstract_expression import AbstractExpression
from typing import List
from src.loaders.abstract_loader import AbstractVideoLoader



class AbstractSelect(AbstractPlan):
    """Abstract class for all the select based planners

    Arguments:
        predicate : Expression
        videos : list of videos on which the select will be executed
        columns_id : columns used in the select in the form of "tablename.attribute"

    """

    def __init__(self, predicate: AbstractExpression, videos: List[AbstractVideoLoader],
                 column_ids: List[str]):
        super(AbstractSelect, self).__init__()
        self._predicate = predicate
        self._column_ids = column_ids
        self._videos = videos

    @property
    def videos(self) -> List[AbstractVideoLoader]:
        return self._videos

    @property
    def predicate(self) -> AbstractExpression:
        return self._predicate

    @property
    def column_ids(self) -> List[str]:
        return self._column_ids

    def __str__(self):
        return 'sigma {}'.format(str(self._predicate))
