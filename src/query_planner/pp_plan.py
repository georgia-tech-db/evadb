from src.expression.abstract_expression import AbstractExpression
from src.query_planner.abstract_scan_plan import AbstractScan
from src.query_planner.types import PlanNodeType


class PPScanPlan(AbstractScan):
    """
    This plan is used for storing information required for probabilistic
    predicate.

    Arguments:
        predicate (AbstractExpression): A predicate expression used for
        filtering frames
    """

    def __init__(self, predicate: AbstractExpression):
        super().__init__(PlanNodeType.PP_FILTER_TYPE, predicate)
