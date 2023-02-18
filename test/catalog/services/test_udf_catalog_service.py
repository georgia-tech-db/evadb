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
from sqlalchemy.orm.exc import NoResultFound

from eva.catalog.services.udf_catalog_service import UdfCatalogService

UDF_TYPE = "classification"
UDF_IMPL_PATH = "file1"
UDF_NAME = "name"
UDF_ID = 123


class UdfCatalogServiceTest(TestCase):
    @patch("eva.catalog.services.udf_catalog_service.UdfCatalog")
    def test_create_udf_should_create_model(self, mocked):
        service = UdfCatalogService()
        service.insert_entry(UDF_NAME, UDF_IMPL_PATH, UDF_TYPE)
        mocked.assert_called_with(UDF_NAME, UDF_IMPL_PATH, UDF_TYPE)
        mocked.return_value.save.assert_called_once()

    @patch("eva.catalog.services.udf_catalog_service.UdfCatalog")
    def test_udf_by_name_should_query_model_with_name(self, mocked):
        service = UdfCatalogService()
        expected = mocked.query.filter.return_value.one.return_value

        actual = service.get_entry_by_name(UDF_NAME)
        mocked.query.filter.assert_called_with(mocked._name == UDF_NAME)
        mocked.query.filter.return_value.one.assert_called_once()
        self.assertEqual(actual, expected.as_dataclass.return_value)

    @patch("eva.catalog.services.udf_catalog_service.UdfCatalog")
    def test_udf_by_id_should_query_model_with_id(self, mocked):
        service = UdfCatalogService()
        expected = mocked.query.filter.return_value.one.return_value
        actual = service.get_entry_by_id(UDF_ID)
        mocked.query.filter.assert_called_with(mocked._id == UDF_ID)
        mocked.query.filter.return_value.one.assert_called_once()
        self.assertEqual(actual, expected.as_dataclass.return_value)

    @patch("eva.catalog.services.udf_catalog_service.UdfCatalog")
    def test_udf_drop_by_name(self, mocked):
        service = UdfCatalogService()
        service.delete_entry_by_name(UDF_NAME)
        udf_obj = mocked.query.filter.return_value.one.return_value
        mocked.query.filter.assert_called_with(mocked._name == UDF_NAME)
        udf_obj.delete.assert_called_once()
        mocked.return_value.delete.side_effect = Exception()
        with self.assertRaises(Exception) as cm:
            service.delete_entry_by_name(UDF_NAME)
            self.assertEqual(
                "Delete udf failed for name {}".format(UDF_NAME),
                str(cm.exception),
            )

    @patch("eva.catalog.services.udf_catalog_service.UdfCatalog")
    def test_get_all_udfs_should_return_empty(self, mocked):
        service = UdfCatalogService()
        mocked.query.all.side_effect = Exception(NoResultFound)
        with self.assertRaises(Exception):
            self.assertEqual(service.get_all_entries(), [])
