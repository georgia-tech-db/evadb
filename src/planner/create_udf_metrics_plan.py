from src.planner.abstract_plan import AbstractPlan
from src.planner.types import PlanNodeType


class CreateUDFMetricsPlan(AbstractPlan):
    def __init__(self,
                 udf_name: str,
                 dataset: str,
                 category: str,
                 precision: float,
                 recall: float):
        super().__init__(PlanNodeType.CREATE_UDF_METRICS)
        self._udf_name = udf_name
        self._dataset = dataset
        self._category = category
        self._precision = precision
        self._recall = recall

    @property
    def udf_name(self):
        return self._udf_name

    @property
    def dataset(self):
        return self._dataset

    @property
    def category(self):
        return self._category

    @property
    def precision(self):
        return self._precision

    @property
    def recall(self):
        return self._recall
