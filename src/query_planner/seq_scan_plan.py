from typing import List

from src.expression.abstract_expression import AbstractExpression
from src.query_planner.abstract_scan_plan import AbstractScan
from src.query_planner.types import PlanNodeType


class SeqScanPlan(AbstractScan):
    """
    This plan is used for storing information required for sequential scan
    operations.

    Arguments:
        predicate (AbstractExpression): A predicate expression used for
        filtering frames

        column_ids List[int]: List of columns which need to be selected
        (Note: This attribute might be removed in future)
    """

    def __init__(self, predicate: AbstractExpression,
                 column_ids: List[int] = None):
        if column_ids is None:
            column_ids = []
        super().__init__(PlanNodeType.SEQUENTIAL_SCAN_TYPE, predicate)
        self._column_ids = column_ids

    @property
    def column_ids(self) -> List:
        return self._column_ids
