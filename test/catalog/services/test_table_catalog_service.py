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

from mock import MagicMock, patch

from eva.catalog.catalog_type import TableType
from eva.catalog.services.table_catalog_service import TableCatalogService

TABLE_ID = 123
TABLE_URL = "file1"
TABLE_NAME = "name"
DATABASE_NAME = "test"
IDENTIFIER = "data_id"
TABLE_NEW_NAME = "new_name"
TABLE_OBJ = "obj"
TABLE_TYPE = TableType.STRUCTURED_DATA


class TableCatalogServiceTest(unittest.TestCase):
    @patch("eva.catalog.services.table_catalog_service.TableCatalog")
    def test_insert_table_catalog_entry(self, mocked):
        mocks = [MagicMock(), MagicMock()]
        with patch(
            "eva.catalog.services.table_catalog_service.ColumnCatalogService"
        ) as col_service:
            service = TableCatalogService()
            service.insert_entry(
                TABLE_NAME,
                TABLE_URL,
                table_type=TABLE_TYPE,
                identifier_column=IDENTIFIER,
                column_list=mocks,
            )
            mocked.assert_called_with(
                name=TABLE_NAME,
                file_url=TABLE_URL,
                identifier_column=IDENTIFIER,
                table_type=TABLE_TYPE,
            )
            col_service.return_value.insert_entries.assert_called_with(mocks)
            mocked.return_value.save.assert_called_once()

    @patch("eva.catalog.services.table_catalog_service.TableCatalog")
    def test_table_catalog_by_id_should_query_model_with_id(self, mocked):
        service = TableCatalogService()
        service.get_entry_by_id(TABLE_ID)
        mocked.query.filter.assert_called_with(mocked._id == TABLE_ID)
        mocked.query.filter.return_value.one.assert_called_once()

    @patch("eva.catalog.services.table_catalog_service.TableCatalog")
    def test_table_catalog_by_name_queries_with_name_returns_model_object(self, mocked):
        service = TableCatalogService()
        actual = service.get_entry_by_name(DATABASE_NAME, TABLE_NAME)
        expected = mocked.query.filter.return_value.one_or_none.return_value

        self.assertEqual(actual, expected.as_dataclass.return_value)
