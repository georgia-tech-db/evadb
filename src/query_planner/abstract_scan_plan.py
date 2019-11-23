"""Abstract class for all the scan planners
https://www.postgresql.org/docs/9.1/using-explain.html
https://www.postgresql.org/docs/9.5/runtime-config-query.html
"""
from src.expression.abstract_expression import AbstractExpression
from src.query_planner.abstract_plan import AbstractPlan

from src.query_planner.types import PlanNodeType


class AbstractScan(AbstractPlan):
    """Abstract class for all the scan based planners
    
    Arguments:
        predicate (AbstractExpression): An expression used for filtering
    """

    def __init__(self, node_type: PlanNodeType, predicate: AbstractExpression):
        super(AbstractScan, self).__init__(node_type)
        self._predicate = predicate

    @property
    def predicate(self) -> 'Expression':
        return self._predicate
