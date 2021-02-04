from src.catalog.models.udf_metrics import UdfMetrics
from src.catalog.services.base_service import BaseService


class UdfMetricsService(BaseService):
    def __init__(self):
        super().__init__(UdfMetrics)

    def create_udf_metrics(self,
                           dataset: str,
                           category: str,
                           precision: float,
                           recall: float,
                           udf_id: int) -> UdfMetrics:
        udf_metrics = self.model(
            dataset, category, precision, recall, udf_id)
        udf_metrics = udf_metrics.save()
        return udf_metrics
