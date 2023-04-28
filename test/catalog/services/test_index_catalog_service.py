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

import pytest
from mock import MagicMock, patch
from sqlalchemy.orm.exc import NoResultFound

from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.catalog_type import ColumnType, IndexType
from eva.catalog.models.column_catalog import ColumnCatalogEntry
from eva.catalog.services.index_catalog_service import IndexCatalogService

INDEX_NAME = "name"
INDEX_ID = 123


@pytest.mark.notparallel
class IndexCatalogServiceTest(TestCase):
    @patch("eva.catalog.services.index_catalog_service.IndexCatalog")
    def test_index_by_name_should_query_model_with_name(self, mocked):
        service = IndexCatalogService()
        expected = mocked.query.filter.return_value.one.return_value

        actual = service.get_entry_by_name(INDEX_NAME)
        mocked.query.filter.assert_called_with(mocked._name == INDEX_NAME)
        mocked.query.filter.return_value.one.assert_called_once()
        self.assertEqual(actual, expected.as_dataclass.return_value)

    @patch("eva.catalog.services.index_catalog_service.IndexCatalog")
    def test_index_by_id_should_query_model_with_id(self, mocked):
        service = IndexCatalogService()
        expected = mocked.query.filter.return_value.one.return_value
        actual = service.get_entry_by_id(INDEX_ID)
        mocked.query.filter.assert_called_with(mocked._id == INDEX_ID)
        mocked.query.filter.return_value.one.assert_called_once()
        self.assertEqual(actual, expected.as_dataclass.return_value)

    @patch("os.remove")
    @patch("os.path.exists")
    def test_index_drop_by_name(self, mock_os_path, mock_os_remove):
        PATCH_PATH = "eva.catalog.services.index_catalog_service.IndexCatalog"

        # file does not exist
        with patch(PATCH_PATH) as mocked:
            service = IndexCatalogService()
            index_obj = mocked.query.filter.return_value.one.return_value
            mock_os_path.return_value = False
            service.delete_entry_by_name(INDEX_NAME)
            mocked.query.filter.assert_called_with(mocked._name == INDEX_NAME)
            index_obj.delete.assert_called_once()

        # file exists
        with patch(PATCH_PATH) as mocked:
            service = IndexCatalogService()
            mock_os_path.return_value = True
            index_obj = mocked.query.filter.return_value.one.return_value
            service.delete_entry_by_name("index_name")
            mocked.query.filter.assert_called_with(mocked._name == INDEX_NAME)
            index_obj.delete.assert_called_once()
            mock_os_remove.assert_called_once_with(
                index_obj.as_dataclass().save_file_path
            )

        with patch(PATCH_PATH) as mocked:
            service = IndexCatalogService()
            index_obj = mocked.query.filter.return_value.one.return_value
            index_obj.delete.side_effect = Exception()
            with self.assertRaises(Exception) as cm:
                service.delete_entry_by_name("index_name")
                self.assertEqual(
                    "Delete index failed for name {}".format("index_name"),
                    str(cm.exception),
                )

    @patch("eva.catalog.services.index_catalog_service.IndexCatalog")
    def test_index_catalog_exception(self, mock_index_catalog):
        mock_index_catalog.query.filter.side_effect = NoResultFound
        mock_index_catalog.query.all.side_effect = NoResultFound

        service = IndexCatalogService()

        self.assertEqual(service.get_entry_by_name(MagicMock()), None)

        self.assertEqual(service.get_entry_by_id(MagicMock()), None)

        self.assertEqual(service.get_all_entries(), [])

    def test_index_get_all_entries(self):
        CatalogManager().reset()
        INDEX_NAME = "name"
        INDEX_URL = "file1"
        INDEX_TYPE = IndexType.HNSW
        FEAT_COLUMN = ColumnCatalogEntry("abc", ColumnType.INTEGER)

        service = IndexCatalogService()

        service.insert_entry(INDEX_NAME, INDEX_URL, INDEX_TYPE, FEAT_COLUMN, "sig")

        output = service.get_all_entries()
        self.assertEqual(len(output), 1)

        service.delete_entry_by_name(INDEX_NAME)
