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
import unittest

from mock import patch

from eva.catalog.catalog_type import TableType
from eva.catalog.services.table_catalog_service import TableCatalogService

DATASET_ID = 123
DATASET_URL = "file1"
DATASET_NAME = "name"
DATABASE_NAME = "test"
IDENTIFIER = "data_id"
DATASET_NEW_NAME = "new_name"
DATASET_OBJ = "obj"
TABLE_TYPE = TableType.STRUCTURED_DATA


class TableCatalogServiceTest(unittest.TestCase):
    @patch("eva.catalog.services.table_catalog_service.TableCatalog")
    def test_create_dataset_should_create_model(self, mocked):
        service = TableCatalogService()
        service.insert_entry(
            DATASET_NAME,
            DATASET_URL,
            table_type=TABLE_TYPE,
            identifier_id=IDENTIFIER,
        )
        mocked.assert_called_with(
            name=DATASET_NAME,
            file_url=DATASET_URL,
            identifier_id=IDENTIFIER,
            table_type=TABLE_TYPE,
        )
        mocked.return_value.save.assert_called_once()

    @patch("eva.catalog.services.table_catalog_service.TableCatalog")
    def test_dataset_by_id_should_query_model_with_id(self, mocked):
        service = TableCatalogService()
        service.get_entry_by_id(DATASET_ID)
        mocked.query.filter.assert_called_with(mocked._id == DATASET_ID)
        mocked.query.filter.return_value.one.assert_called_once()

    @patch("eva.catalog.services.table_catalog_service.TableCatalog")
    def test_dataset_object_by_name_queries_with_name_returns_model_object(
        self, mocked
    ):
        service = TableCatalogService()
        actual = service.get_entry_by_name(DATABASE_NAME, DATASET_NAME)
        expected = mocked.query.filter.return_value.one_or_none.return_value

        self.assertEqual(actual, expected)
