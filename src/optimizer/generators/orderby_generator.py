from src.optimizer.generators.base import Generator
from src.optimizer.operators import LogicalOrderBy, Operator
from src.planner.orderby_plan import OrderByPlan


class OrderByGenerator(Generator):
    def __init__(self):
        self._orderby_list = None

    def _visit(self, operator: Operator):
        if isinstance(operator, LogicalOrderBy):
            self._orderby_list = operator.orderby_list

    def build(self, operator: Operator):
        self.__init__()
        self._visit(operator)
        orderby_plan = OrderByPlan(self._orderby_list)
        return orderby_plan
