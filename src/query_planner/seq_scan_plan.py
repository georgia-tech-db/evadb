from typing import List

from src.expression.abstract_expression import AbstractExpression
from src.query_planner.abstract_scan_plan import AbstractScan
from src.query_planner.types import PlanNodeType


class SeqScanPlan(AbstractScan):
    def __init__(self, predicate: AbstractExpression,
                 column_ids: List[int] = None):
        if column_ids is None:
            column_ids = []
        super().__init__(PlanNodeType.SEQUENTIAL_SCAN_TYPE, predicate,
                         column_ids)
