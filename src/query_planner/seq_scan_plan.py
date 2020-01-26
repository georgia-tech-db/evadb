from typing import List

from src.expression.abstract_expression import AbstractExpression
from src.query_planner.abstract_scan_plan import AbstractScan
from src.query_planner.types import PlanNodeType


class SeqScanPlan(AbstractScan):
    """
    This plan is used for storing information required for sequential scan
    operations.

    Arguments:
        column_ids: List[str] 
            list of column names string in the plan
        video: TableRef
            video reference for the plan
        predicate: AbstractExpression
            An expression used for filtering
    """

    def __init__(self, column_ids: List[str], video: TableRef, predicate: AbstractExpression,
                  ):
        super().__init__(PlanNodeType.SEQUENTIAL_SCAN_TYPE, column_ids, video, predicate)

    