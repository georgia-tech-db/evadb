from typing import List

from src.expression.abstract_expression import AbstractExpression
from src.loaders.abstract_loader import AbstractVideoLoader
from src.query_planner.abstract_scan_plan import AbstractScan
from src.query_planner.abstract_plan import PlanNodeType


class SeqScanPlan(AbstractScan):
    def __init__(self, predicate: AbstractExpression,
                 video: AbstractVideoLoader,
                 column_ids: List[int]):
        super().__init__(predicate, video, column_ids)

    def get_node_type(self):
        return PlanNodeType.SEQSCAN

    # ToDo Add other functionality based on optimiser
