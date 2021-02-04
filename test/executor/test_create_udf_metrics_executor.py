import unittest
from mock import patch
from src.executor.create_udf_metrics_executor import CreateUDFMetricsExecutor


class CreateUdfMetricsExecutorTest(unittest.TestCase):
    @patch('src.executor.create_udf_metrics_executor.CatalogManager')
    def test_should_create_udf_metrics(self, mock):
        catalog_instance = mock.return_value
        plan = type("CreateUDFMetricsPlan",
                    (),
                    {'udf_name': 'name',
                     'dataset': 'dataset',
                     'category': 'category',
                     'precision': 0.1,
                     'recall': 0.2})

        create_udf_metrics_executor = CreateUDFMetricsExecutor(plan)
        create_udf_metrics_executor.exec()
        catalog_instance.create_udf_metrics.assert_called_with(
            'name', 'dataset', 'category', 0.1, 0.2)
