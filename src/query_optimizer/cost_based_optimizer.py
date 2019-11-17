"""Cost based Optimizer for Eva"""
from src.expression.abstract_expression import AbstractExpression
from .pp_optmizer import PPOptmizer
from src.catalog.catalog import Catalog


class CostBasedOptimizer:

    def __init__(self, dataset: str, query_expression: AbstractExpression):
        self._predicates = query_expression.predicates
        self._catalog = Catalog(dataset)

    def execute(self):
        pp_optmizer = PPOptmizer(self._catalog, self._predicates)
        optimizer_results  = pp_optmizer.execute()
