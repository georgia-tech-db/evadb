from src.optimizer.generators.base import Generator
from src.optimizer.operators import LogicalCreateUDFMetrics, Operator
from src.planner.create_udf_metrics_plan import CreateUDFMetricsPlan


class CreateUDFMetricsGenerator(Generator):
    def __init__(self):
        self._udf_name = None
        self._dataset = None
        self._category = None
        self._precision = None
        self._recall = None

    def _visit_logical_create_udf_metrics(self,
                                          operator: LogicalCreateUDFMetrics):
        self._udf_name = operator.udf_name
        self._dataset = operator.dataset
        self._category = operator.category
        self._precision = operator.precision
        self._recall = operator.recall

    def _visit(self, operator: Operator):
        if isinstance(operator, LogicalCreateUDFMetrics):
            self._visit_logical_create_udf_metrics(operator)

    def build(self, operator: Operator):
        self.__init__()
        self._visit(operator)
        create_udf_metrics_plan = CreateUDFMetricsPlan(
            self._udf_name,
            self._dataset,
            self._category,
            self._precision,
            self._recall)
        return create_udf_metrics_plan
