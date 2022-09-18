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

from mock import MagicMock, call, patch

from eva.binder.binder_utils import (
    BinderError,
    bind_table_info,
    create_video_metadata,
    handle_if_not_exists,
)
from eva.catalog.column_type import ColumnType, NdArrayType


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

    @patch("eva.binder.binder_utils.CatalogManager")
    @patch("eva.binder.binder_utils.ColumnDefinition")
    @patch("eva.binder.binder_utils.ColConstraintInfo")
    @patch("eva.binder.binder_utils.create_column_metadata")
    @patch("eva.binder.binder_utils.generate_file_path")
    def test_create_video_metadata(self, m_gfp, m_ccm, m_cci, m_cd, m_cm):
        catalog_ins = MagicMock()
        expected = "video_metadata"
        name = "eva"
        uri = "tmp"
        m_gfp.return_value = uri
        m_ccm.return_value = "col_metadata"
        m_cci.return_value = "cci"
        m_cd.return_value = 1
        m_cm.return_value = catalog_ins
        catalog_ins.create_metadata.return_value = expected

        calls = [
            call("name", ColumnType.TEXT, None, [], "cci"),
            call("id", ColumnType.INTEGER, None, []),
            call("data", ColumnType.NDARRAY, NdArrayType.UINT8, [None, None, None]),
        ]

        actual = create_video_metadata(name)
        m_gfp.assert_called_once_with(name)
        m_ccm.assert_called_once_with([1, 1, 1])
        m_cci.assert_called_once_with(unique=True)
        m_cd.assert_has_calls(calls)
        catalog_ins.create_metadata.assert_called_with(
            name, uri, "col_metadata", identifier_column="id", is_video=True
        )
        self.assertEqual(actual, expected)

    @patch("eva.binder.binder_utils.CatalogManager.check_table_exists")
    def test_handle_if_not_exists_raises_error(self, check_mock):
        check_mock.return_value = True
        with self.assertRaises(BinderError):
            handle_if_not_exists(check_mock, False)

    @patch("eva.binder.binder_utils.CatalogManager.check_table_exists")
    def test_handle_if_not_exists_return_True(self, check_mock):
        check_mock.return_value = True
        self.assertTrue(handle_if_not_exists(check_mock, True))
