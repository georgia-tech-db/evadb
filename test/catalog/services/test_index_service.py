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

from eva.catalog.services.index_service import IndexService

INDEX_TYPE = "HSNW"
INDEX_IMPL_PATH = "file1"
INDEX_NAME = "name"
INDEX_ID = 123


class IndexServiceTest(TestCase):
    @patch("eva.catalog.services.index_service.IndexCatalog")
    def test_create_index_should_create_model(self, mocked):
        service = IndexService()
        service.create_index(INDEX_NAME, INDEX_IMPL_PATH, INDEX_TYPE)
        mocked.assert_called_with(INDEX_NAME, INDEX_IMPL_PATH, INDEX_TYPE)
        mocked.return_value.save.assert_called_once()

    @patch("eva.catalog.services.index_service.IndexCatalog")
    def test_index_by_name_should_query_model_with_name(self, mocked):
        service = IndexService()
        expected = mocked.query.filter.return_value.one.return_value

        actual = service.index_by_name(INDEX_NAME)
        mocked.query.filter.assert_called_with(mocked._name == INDEX_NAME)
        mocked.query.filter.return_value.one.assert_called_once()
        self.assertEqual(actual, expected)

    @patch("eva.catalog.services.index_service.IndexCatalog")
    def test_index_by_id_should_query_model_with_id(self, mocked):
        service = IndexService()
        expected = mocked.query.filter.return_value.one.return_value
        actual = service.index_by_id(INDEX_ID)
        mocked.query.filter.assert_called_with(mocked._id == INDEX_ID)
        mocked.query.filter.return_value.one.assert_called_once()
        self.assertEqual(actual, expected)

    @patch("os.remove")
    @patch("os.path.exists")
    def test_index_drop_by_name(self, mock_os_path, mock_os_remove):
        service = IndexService()

        # file does not exist
        with patch(
            "eva.catalog.services.index_service.IndexService.index_by_name"
        ) as mock_func:
            mock_os_path.return_value = False
            service.drop_index_by_name("index_name")
            mock_func.assert_called_once_with("index_name")
            mock_func.return_value.delete.assert_called_once()

        # file exists
        with patch(
            "eva.catalog.services.index_service.IndexService.index_by_name"
        ) as mock_func:
            mock_os_path.return_value = True
            save_file_path = mock_func.return_value.save_file_path
            service.drop_index_by_name("index_name")
            mock_func.assert_called_once_with("index_name")
            mock_func.return_value.delete.assert_called_once()
            mock_os_remove.assert_called_once_with(save_file_path)

        with patch(
            "eva.catalog.services.index_service.IndexService.index_by_name"
        ) as mock_func:
            mock_func.return_value.delete.side_effect = Exception()
            with self.assertRaises(Exception) as cm:
                service.drop_index_by_name("index_name")
                self.assertEqual(
                    "Delete index failed for name {}".format("index_name"),
                    str(cm.exception),
                )

    @patch("eva.catalog.services.index_service.IndexCatalog")
    def test_get_all_indices_should_return_empty(self, mocked):
        service = IndexService()
        mocked.query.all.side_effect = Exception(NoResultFound)
        with self.assertRaises(Exception):
            self.assertEqual(service.get_all_indexs(), [])
