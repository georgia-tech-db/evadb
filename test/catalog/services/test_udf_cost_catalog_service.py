# coding=utf-8
# Copyright 2018-2022 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from unittest import TestCase

from mock import patch

from eva.catalog.services.udf_cost_catalog_service import UdfCostCatalogService
from eva.utils.errors import CatalogError

UDF_ID = 123
UDF_NAME = "name"
UDF_COST = 1


class UdfCostCatalogServiceTest(TestCase):
    @patch("eva.catalog.services.udf_cost_catalog_service.UdfCostCatalog")
    def test_create_udf_should_create_model(self, mocked):
        service = UdfCostCatalogService()
        service.insert_entry(UDF_ID, UDF_NAME, UDF_COST)
        mocked.assert_called_with(UDF_ID, UDF_NAME, UDF_COST)
        mocked.return_value.save.assert_called_once()

    @patch("eva.catalog.services.udf_cost_catalog_service.UdfCostCatalog")
    def test_udf_by_name_should_query_model_with_name(self, mocked):
        service = UdfCostCatalogService()
        expected = mocked.query.filter.return_value.one_or_none.return_value
        actual = service.get_entry_by_name(UDF_NAME)
        mocked.query.filter.assert_called_with(mocked._udf_name == UDF_NAME)
        mocked.query.filter.return_value.one_or_none.assert_called_once()
        self.assertEqual(actual, expected.as_dataclass.return_value)

    @patch("eva.catalog.services.udf_cost_catalog_service.UdfCostCatalog")
    def test_insert_should_raise_exception(self, mock):
        service = UdfCostCatalogService()
        mock.side_effect = Exception("exception")
        with self.assertRaises(CatalogError) as cm:
            service.insert_entry(UDF_ID, UDF_NAME, UDF_COST)
        self.assertEqual(
            str(cm.exception),
            "Error while inserting entry to UdfCostCatalog: exception",
        )

    @patch("eva.catalog.services.udf_cost_catalog_service.UdfCostCatalog")
    def test_upsert_entry_should_raise_exception(self, mock):
        service = UdfCostCatalogService()
        mock.query.filter.side_effect = Exception("exception")
        with self.assertRaises(CatalogError) as cm:
            service.upsert_entry(UDF_ID, UDF_NAME, UDF_COST)
        self.assertEqual(
            str(cm.exception),
            "Error while upserting entry to UdfCostCatalog: exception",
        )

    @patch("eva.catalog.services.udf_cost_catalog_service.UdfCostCatalog")
    def test_get_entry_should_raise_exception(self, mock):
        service = UdfCostCatalogService()
        mock.query.filter.side_effect = Exception("exception")
        with self.assertRaises(CatalogError) as cm:
            service.get_entry_by_name(UDF_NAME)
        self.assertEqual(
            str(cm.exception),
            f"Error while getting entry for udf {UDF_NAME} from UdfCostCatalog: exception",
        )
