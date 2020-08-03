# coding=utf-8
# Copyright 2018-2020 EVA
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
from mock import MagicMock
from src.catalog.catalog_manager import CatalogManager
from src.catalog.column_type import ColumnType
from src.catalog.models.df_column import DataFrameColumn


class CatalogManagerTests(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @mock.patch('src.catalog.catalog_manager.init_db')
    def test_catalog_manager_singleton_pattern(self, mocked_db):
        x = CatalogManager()
        y = CatalogManager()
        self.assertEqual(x, y)

    @mock.patch('src.catalog.catalog_manager.init_db')
    def test_catalog_bootstrap(self, mocked_db):
        x = CatalogManager()
        x._bootstrap_catalog()
        mocked_db.assert_called()

    @mock.patch('src.catalog.catalog_manager.drop_db')
    def test_catalog_shutdown(self, mocked_db):
        x = CatalogManager()
        x._shutdown_catalog()
        mocked_db.assert_called_once()

    @mock.patch('src.catalog.catalog_manager.CatalogManager._shutdown_catalog')
    @mock.patch('src.catalog.catalog_manager.CatalogManager._bootstrap_catalog')  # noqa
    def test_catalog_manager_reset(self, mock_bootstrap, mock_shutdown):
        x = CatalogManager()
        mock_init = MagicMock()
        with mock.patch.object(CatalogManager, '__init__', mock_init):
            x.reset()
            mock_init.assert_called_once_with()
            mock_bootstrap.assert_called_once_with()
            mock_shutdown.assert_called_once_with()

    @mock.patch('src.catalog.catalog_manager.init_db')
    @mock.patch('src.catalog.catalog_manager.DatasetService')
    @mock.patch('src.catalog.catalog_manager.DatasetColumnService')
    def test_create_metadata_should_create_dataset_and_columns(self, dcs_mock,
                                                               ds_mock,
                                                               initdb_mock):
        catalog = CatalogManager()
        file_url = "file1"
        dataset_name = "name"

        columns = [(DataFrameColumn("c1", ColumnType.INTEGER))]
        actual = catalog.create_metadata(dataset_name, file_url, columns)
        ds_mock.return_value.create_dataset.assert_called_with(
            dataset_name, file_url, identifier_id='id')
        for column in columns:
            column.metadata_id = \
                ds_mock.return_value.create_dataset.return_value.id

        dcs_mock.return_value.create_column.assert_called_with(columns)

        expected = ds_mock.return_value.create_dataset.return_value
        expected.schema = \
            dcs_mock.return_value.create_column.return_value

        self.assertEqual(actual, expected)

    @mock.patch('src.catalog.catalog_manager.init_db')
    @mock.patch('src.catalog.catalog_manager.DatasetService')
    @mock.patch('src.catalog.catalog_manager.DatasetColumnService')
    def test_table_binding_returns_metadata_and_column_ids(self,
                                                           dcs_mock,
                                                           ds_mock,
                                                           initdb_mock):
        catalog = CatalogManager()
        dataset_name = "name"

        columns = ["column1", "column2"]
        database_name = "database"
        actual = catalog.get_table_bindings(database_name, dataset_name,
                                            columns)
        ds_dataset_name_mock = ds_mock.return_value.dataset_by_name
        ds_dataset_name_mock.assert_called_with(dataset_name)

        column_values_mock = \
            dcs_mock.return_value.columns_by_dataset_id_and_names
        column_values_mock.assert_called_with(
            ds_dataset_name_mock.return_value,
            columns
        )

        self.assertEqual(actual, (ds_dataset_name_mock.return_value,
                                  column_values_mock.return_value))

    @mock.patch('src.catalog.catalog_manager.init_db')
    @mock.patch('src.catalog.catalog_manager.DatasetService')
    @mock.patch('src.catalog.catalog_manager.DatasetColumnService')
    def test_table_binding_without_columns_returns_no_column_ids(self,
                                                                 dcs_mock,
                                                                 ds_mock,
                                                                 initdb_mock):
        catalog = CatalogManager()
        dataset_name = "name"

        database_name = "database"
        actual = catalog.get_table_bindings(database_name, dataset_name)
        ds_dataset_name_mock = ds_mock.return_value.dataset_by_name
        ds_dataset_name_mock.assert_called_with(dataset_name)

        column_values_mock = \
            dcs_mock.return_value.columns_by_dataset_id_and_names
        column_values_mock.assert_not_called()

        self.assertEqual(actual, (ds_dataset_name_mock.return_value, []))

    @mock.patch('src.catalog.catalog_manager.init_db')
    @mock.patch('src.catalog.catalog_manager.DatasetService')
    @mock.patch('src.catalog.catalog_manager.DatasetColumnService')
    def test_get_dataset_metadata_when_table_exists(self,
                                                    dcs_mock,
                                                    ds_mock,
                                                    initdb_mock):
        catalog = CatalogManager()
        dataset_name = "name"

        database_name = "database"
        schema = [1, 2, 3]
        id = 1
        metadata_obj = MagicMock(id=id, schema=None)
        ds_mock.return_value.dataset_object_by_name.return_value = metadata_obj
        dcs_mock.return_value. \
            columns_by_id_and_dataset_id.return_value = schema

        actual = catalog.get_dataset_metadata(database_name, dataset_name)
        ds_mock.return_value.dataset_object_by_name.assert_called_with(
            database_name, dataset_name)
        dcs_mock.return_value.columns_by_id_and_dataset_id.assert_called_with(
            id, None)
        self.assertEqual(actual.id, id)
        self.assertEqual(actual.schema, schema)

    @mock.patch('src.catalog.catalog_manager.init_db')
    @mock.patch('src.catalog.catalog_manager.DatasetService')
    @mock.patch('src.catalog.catalog_manager.DatasetColumnService')
    def test_get_dataset_metadata_when_table_doesnot_exists(self,
                                                            dcs_mock,
                                                            ds_mock,
                                                            initdb_mock):
        catalog = CatalogManager()
        dataset_name = "name"

        database_name = "database"
        metadata_obj = None

        ds_mock.return_value.dataset_object_by_name.return_value = metadata_obj

        actual = catalog.get_dataset_metadata(database_name, dataset_name)
        ds_mock.return_value.dataset_object_by_name.assert_called_with(
            database_name, dataset_name)
        dcs_mock.return_value.columns_by_id_and_dataset_id.assert_not_called()
        self.assertEqual(actual, metadata_obj)

    @mock.patch('src.catalog.catalog_manager.UdfIO')
    def test_create_udf_io_object(self, udfio_mock):
        catalog = CatalogManager()
        actual = catalog.udf_io('name', ColumnType.TEXT, [100], True)
        udfio_mock.assert_called_with(
            'name',
            ColumnType.TEXT,
            array_dimensions=[100],
            is_input=True)
        self.assertEqual(actual, udfio_mock.return_value)

    @mock.patch('src.catalog.catalog_manager.UdfService')
    @mock.patch('src.catalog.catalog_manager.UdfIOService')
    def test_create_udf(self, udfio_mock, udf_mock):
        catalog = CatalogManager()
        udf_io_list = [MagicMock()]
        actual = catalog.create_udf(
            'udf', 'sample.py', 'classification', udf_io_list)
        udfio_mock.return_value.add_udf_io.assert_called_with(udf_io_list)
        udf_mock.return_value.create_udf.assert_called_with(
            'udf', 'sample.py', 'classification')
        self.assertEqual(actual, udf_mock.return_value.create_udf.return_value)

    @mock.patch('src.catalog.catalog_manager.init_db')
    @mock.patch('src.catalog.catalog_manager.DatasetService')
    @mock.patch('src.catalog.catalog_manager.DatasetColumnService')
    def test_delete_metadata(self, dcs_mock, ds_mock, initdb_mock):
        dataset_name = "name"
        catalog = CatalogManager()
        catalog.delete_metadata(dataset_name)
        ds_id_mock = ds_mock.return_value.dataset_by_name
        ds_id_mock.assert_called_with(dataset_name)
        ds_mock.return_value.delete_dataset_by_id.assert_called_with(
            ds_id_mock.return_value)

    @mock.patch('src.catalog.catalog_manager.UdfService')
    def test_get_udf_by_name(self, udf_mock):
        catalog = CatalogManager()
        actual = catalog.get_udf_by_name('name')
        udf_mock.return_value.udf_by_name.assert_called_with('name')
        self.assertEqual(actual,
                         udf_mock.return_value.udf_by_name.return_value)

    @mock.patch('src.catalog.catalog_manager.UdfService')
    def test_delete_udf(self, udf_mock):
        actual = CatalogManager().delete_udf('name')
        udf_mock.return_value.delete_udf_by_name.assert_called_with('name')
        self.assertEqual(
            udf_mock.return_value.delete_udf_by_name.return_value,
            actual)
