# coding=utf-8
# Copyright 2018-2023 EvaDB
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

import mock
import pytest
from mock import ANY, MagicMock

from evadb.catalog.catalog_manager import CatalogManager
from evadb.catalog.catalog_type import ColumnType, TableType
from evadb.catalog.catalog_utils import get_video_table_column_definitions
from evadb.catalog.models.column_catalog import ColumnCatalogEntry
from evadb.catalog.models.udf_catalog import UdfCatalogEntry
from evadb.parser.table_ref import TableInfo
from evadb.parser.types import FileFormatType


@pytest.mark.notparallel
class CatalogManagerTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls) -> None:
        cls.mocks = [
            mock.patch("evadb.catalog.catalog_manager.SQLConfig"),
            mock.patch("evadb.catalog.catalog_manager.init_db"),
        ]
        for single_mock in cls.mocks:
            single_mock.start()
            cls.addClassCleanup(single_mock.stop)

    @mock.patch("evadb.catalog.catalog_manager.init_db")
    def test_catalog_bootstrap(self, mocked_db):
        x = CatalogManager(MagicMock(), MagicMock())
        x._bootstrap_catalog()
        mocked_db.assert_called()

    @mock.patch(
        "evadb.catalog.catalog_manager.CatalogManager.create_and_insert_table_catalog_entry"
    )
    def test_create_multimedia_table_catalog_entry(self, mock):
        x = CatalogManager(MagicMock(), MagicMock())
        name = "myvideo"
        x.create_and_insert_multimedia_table_catalog_entry(
            name=name, format_type=FileFormatType.VIDEO
        )

        columns = get_video_table_column_definitions()

        mock.assert_called_once_with(
            TableInfo(name),
            columns,
            table_type=TableType.VIDEO_DATA,
        )

    @mock.patch("evadb.catalog.catalog_manager.init_db")
    @mock.patch("evadb.catalog.catalog_manager.TableCatalogService")
    def test_insert_table_catalog_entry_should_create_table_and_columns(
        self, ds_mock, initdb_mock
    ):
        catalog = CatalogManager(MagicMock(), MagicMock())
        file_url = "file1"
        table_name = "name"

        columns = [(ColumnCatalogEntry("c1", ColumnType.INTEGER))]
        catalog.insert_table_catalog_entry(table_name, file_url, columns)
        ds_mock.return_value.insert_entry.assert_called_with(
            table_name,
            file_url,
            identifier_column="id",
            table_type=TableType.VIDEO_DATA,
            column_list=[ANY] + columns,
        )

    @mock.patch("evadb.catalog.catalog_manager.init_db")
    @mock.patch("evadb.catalog.catalog_manager.TableCatalogService")
    def test_get_table_catalog_entry_when_table_exists(self, ds_mock, initdb_mock):
        catalog = CatalogManager(MagicMock(), MagicMock())
        table_name = "name"
        database_name = "database"
        row_id = 1
        table_obj = MagicMock(row_id=row_id)
        ds_mock.return_value.get_entry_by_name.return_value = table_obj

        actual = catalog.get_table_catalog_entry(
            table_name,
            database_name,
        )
        ds_mock.return_value.get_entry_by_name.assert_called_with(
            database_name, table_name
        )
        self.assertEqual(actual.row_id, row_id)

    @mock.patch("evadb.catalog.catalog_manager.init_db")
    @mock.patch("evadb.catalog.catalog_manager.TableCatalogService")
    @mock.patch("evadb.catalog.catalog_manager.ColumnCatalogService")
    def test_get_table_catalog_entry_when_table_doesnot_exists(
        self, dcs_mock, ds_mock, initdb_mock
    ):
        catalog = CatalogManager(MagicMock(), MagicMock())
        table_name = "name"

        database_name = "database"
        table_obj = None

        ds_mock.return_value.get_entry_by_name.return_value = table_obj

        actual = catalog.get_table_catalog_entry(table_name, database_name)
        ds_mock.return_value.get_entry_by_name.assert_called_with(
            database_name, table_name
        )
        dcs_mock.return_value.filter_entries_by_table_id.assert_not_called()
        self.assertEqual(actual, table_obj)

    @mock.patch("evadb.catalog.catalog_manager.UdfCatalogService")
    @mock.patch("evadb.catalog.catalog_manager.UdfIOCatalogService")
    @mock.patch("evadb.catalog.catalog_manager.UdfMetadataCatalogService")
    @mock.patch("evadb.catalog.catalog_manager.get_file_checksum")
    def test_insert_udf(self, checksum_mock, udfmetadata_mock, udfio_mock, udf_mock):
        catalog = CatalogManager(MagicMock(), MagicMock())
        udf_io_list = [MagicMock()]
        udf_metadata_list = [MagicMock()]
        actual = catalog.insert_udf_catalog_entry(
            "udf", "sample.py", "classification", udf_io_list, udf_metadata_list
        )
        udfio_mock.return_value.insert_entries.assert_called_with(udf_io_list)
        udfmetadata_mock.return_value.insert_entries.assert_called_with(
            udf_metadata_list
        )
        udf_mock.return_value.insert_entry.assert_called_with(
            "udf", "sample.py", "classification", checksum_mock.return_value
        )
        checksum_mock.assert_called_with("sample.py")
        self.assertEqual(actual, udf_mock.return_value.insert_entry.return_value)

    @mock.patch("evadb.catalog.catalog_manager.UdfCatalogService")
    def test_get_udf_catalog_entry_by_name(self, udf_mock):
        catalog = CatalogManager(MagicMock(), MagicMock())
        actual = catalog.get_udf_catalog_entry_by_name("name")
        udf_mock.return_value.get_entry_by_name.assert_called_with("name")
        self.assertEqual(actual, udf_mock.return_value.get_entry_by_name.return_value)

    @mock.patch("evadb.catalog.catalog_manager.UdfCatalogService")
    def test_delete_udf(self, udf_mock):
        CatalogManager(MagicMock(), MagicMock()).delete_udf_catalog_entry_by_name(
            "name"
        )
        udf_mock.return_value.delete_entry_by_name.assert_called_with("name")

    @mock.patch("evadb.catalog.catalog_manager.UdfIOCatalogService")
    def test_get_udf_outputs(self, udf_mock):
        mock_func = udf_mock.return_value.get_output_entries_by_udf_id
        udf_obj = MagicMock(spec=UdfCatalogEntry)
        CatalogManager(MagicMock(), MagicMock()).get_udf_io_catalog_output_entries(
            udf_obj
        )
        mock_func.assert_called_once_with(udf_obj.row_id)

    @mock.patch("evadb.catalog.catalog_manager.UdfIOCatalogService")
    def test_get_udf_inputs(self, udf_mock):
        mock_func = udf_mock.return_value.get_input_entries_by_udf_id
        udf_obj = MagicMock(spec=UdfCatalogEntry)
        CatalogManager(MagicMock(), MagicMock()).get_udf_io_catalog_input_entries(
            udf_obj
        )
        mock_func.assert_called_once_with(udf_obj.row_id)
