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

from mock import MagicMock, PropertyMock, patch

from eva.binder.binder_utils import BinderError, bind_table_info
from eva.catalog.catalog_type import TableType


class BinderUtilsTest(unittest.TestCase):
    @patch("eva.binder.binder_utils.CatalogManager")
    def test_bind_table_info(self, mock):
        video = MagicMock()
        catalog = mock.return_value
        catalog.get_table_catalog_entry.return_value = obj = MagicMock()
        bind_table_info(video)
        catalog.get_table_catalog_entry.assert_called_with(
            video.table_name,
            video.database_name,
        )
        self.assertEqual(video.table_obj, obj)

    @patch("eva.binder.binder_utils.CatalogManager")
    def test_bind_table_info_raise(self, mock):
        with self.assertRaises(BinderError):
            video = MagicMock()
            catalog = mock.return_value
            catalog.get_table_catalog_entry.return_value = None
            bind_table_info(video)

    @patch("eva.binder.binder_utils.CatalogManager")
    def test_bind_table_info_raise_for_system_tables(self, mock):
        video = MagicMock()
        catalog = mock.return_value
        obj = MagicMock()
        catalog.get_table_catalog_entry.return_value = obj
        type(obj).table_type = PropertyMock(
            return_value=TableType.SYSTEM_STRUCTURED_DATA
        )
        with self.assertRaises(BinderError):
            bind_table_info(video)
