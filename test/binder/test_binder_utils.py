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

from eva.binder.binder_utils import BinderError, bind_table_info, handle_if_not_exists


class BinderUtilsTest(unittest.TestCase):
    @patch("eva.binder.binder_utils.CatalogManager")
    def test_bind_table_info(self, mock):
        video = MagicMock()
        catalog = mock.return_value
        catalog.get_dataset_metadata.return_value = "obj"
        bind_table_info(video)
        catalog.get_dataset_metadata.assert_called_with(
            video.database_name, video.table_name
        )
        self.assertEqual(video.table_obj, "obj")

    @patch("eva.binder.binder_utils.CatalogManager")
    def test_bind_table_info_raise(self, mock):
        with self.assertRaises(BinderError):
            video = MagicMock()
            catalog = mock.return_value
            catalog.get_dataset_metadata.return_value = None
            bind_table_info(video)

    @patch("eva.binder.binder_utils.CatalogManager.check_table_exists")
    def test_handle_if_not_exists_raises_error(self, check_mock):
        check_mock.return_value = True
        with self.assertRaises(BinderError):
            handle_if_not_exists(check_mock, False)

    @patch("eva.binder.binder_utils.CatalogManager.check_table_exists")
    def test_handle_if_not_exists_return_True(self, check_mock):
        check_mock.return_value = True
        self.assertTrue(handle_if_not_exists(check_mock, True))
