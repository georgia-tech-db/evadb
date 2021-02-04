from src.catalog.catalog_manager import CatalogManager
from src.executor.abstract_executor import AbstractExecutor
from src.planner.create_udf_metrics_plan import CreateUDFMetricsPlan


class CreateUDFMetricsExecutor(AbstractExecutor):

    def __init__(self, node: CreateUDFMetricsPlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self):
        CatalogManager().create_udf_metrics(
            self.node.udf_name,
            self.node.dataset,
            self.node.category,
            self.node.precision,
            self.node.recall)
