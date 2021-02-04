from unittest import TestCase

from mock import patch

from src.catalog.services.udf_metrics_service import UdfMetricsService


class UdfMetricsServiceTest(TestCase):

    @patch("src.catalog.services.udf_metrics_service.UdfMetrics")
    def test_create_udf_metrics_should_create_model(self, mocked):
        service = UdfMetricsService()
        service.create_udf_metrics(
            'dataset',
            'category',
            0.1,
            0.2,
            123456)
        mocked.assert_called_with(
            'dataset',
            'category',
            0.1,
            0.2,
            123456)
        mocked.return_value.save.assert_called_once()
