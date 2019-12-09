"""Cost based Optimizer for Eva"""

import logging

from src.catalog.catalog import Catalog
from src.query_optimizer.pp_optimizer import PPOptimizer
from src.query_planner.abstract_plan import AbstractPlan
from src.query_planner.logical_projection_plan import LogicalProjectionPlan
from src.query_planner.logical_select_plan import LogicalSelectPlan


class CostBasedOptimizer:
    def __init__(self, dataset: str):
        self._catalog = Catalog(dataset)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def execute(self, node: AbstractPlan):
        pp_optimizer = PPOptimizer(self._catalog)
        for ind, child in enumerate(node.children):
            if type(child) == LogicalSelectPlan or \
                    type(child) == LogicalProjectionPlan:
                if child.predicate:
                    optimized_predicate, cost = \
                        pp_optimizer.execute(child.predicate)
                    self.logger.info(
                        "Optimized predicate from "
                        + str(child.predicate)
                        + " to "
                        + str(optimized_predicate)
                        + " with cost "
                        + str(cost)
                    )
                    child.set_predicate(optimized_predicate)
                    self.execute(child)
        return node
