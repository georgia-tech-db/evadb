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

from eva.catalog.services.udf_io_catalog_service import UdfIOCatalogService

UDF_TYPE = "classification"
UDF_IMPL_PATH = "file1"
UDF_NAME = "name"
UDF_ID = 123


class UdfCatalogServiceTest(TestCase):
    @patch("eva.catalog.services.udf_io_catalog_service.UdfIOCatalog")
    def test_get_inputs_by_udf_id_should_query_model_with_id(self, mocked):
        service = UdfIOCatalogService()

        service.get_input_entries_by_udf_id(UDF_ID)
        mocked.query.filter.assert_called_with(
            mocked._id == UDF_ID, mocked._is_input == True  # noqa
        )
        mocked.query.filter.return_value.all.assert_called_once()

    @patch("eva.catalog.services.udf_io_catalog_service.UdfIOCatalog")
    def test_get_inputs_by_udf_id_should_raise(self, mock):
        service = UdfIOCatalogService()
        mock.query.filter.side_effect = Exception("error")
        with self.assertRaises(Exception) as cm:
            service.get_input_entries_by_udf_id(UDF_ID)
        self.assertEqual(
            f"Getting inputs for UDF id {UDF_ID} raised error", str(cm.exception)
        )

    @patch("eva.catalog.services.udf_io_catalog_service.UdfIOCatalog")
    def test_get_outputs_by_udf_id_should_query_model_with_id(self, mocked):
        service = UdfIOCatalogService()

        service.get_output_entries_by_udf_id(UDF_ID)
        mocked.query.filter.assert_called_with(
            mocked._id == UDF_ID, mocked._is_input == False  # noqa
        )
        mocked.query.filter.return_value.all.assert_called_once()

    @patch("eva.catalog.services.udf_io_catalog_service.UdfIOCatalog")
    def test_get_outputs_by_udf_id_should_raise(self, mock):
        service = UdfIOCatalogService()
        mock.query.filter.side_effect = Exception("error")
        with self.assertRaises(Exception) as cm:
            service.get_output_entries_by_udf_id(UDF_ID)
        self.assertEqual(
            f"Getting outputs for UDF id {UDF_ID} raised error", str(cm.exception)
        )
