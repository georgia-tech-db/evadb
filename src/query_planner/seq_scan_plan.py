from typing import List

from src.expression.abstract_expression import AbstractExpression
from src.loaders.abstract_loader import AbstractVideoLoader
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
                 videos: List[AbstractVideoLoader],
                 column_ids: List[str], foreign_column_ids: List[str]):
        super().__init__(predicate, videos, column_ids, foreign_column_ids)

    def get_node_type(self):
        return PlanNodeType.SEQUENTIAL_SCAN_TYPE
