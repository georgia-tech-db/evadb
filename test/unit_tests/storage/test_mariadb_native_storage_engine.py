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

import sys
import unittest
from test.util import get_evadb_for_testing
from unittest.mock import MagicMock, patch

import pytest

from evadb.catalog.models.utils import DatabaseCatalogEntry
from evadb.server.command_handler import execute_query_fetch_all


class NativeQueryResponse:
    def __init__(self):
        self.error = None
        self.data = None


@pytest.mark.notparallel
class MariaDbStorageEngineTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_mariadb_params(self):
        return {"user": "eva", "password": "password", "database": "evadb"}

    def setUp(self):
        connection_params = self.get_mariadb_params()
        self.evadb = get_evadb_for_testing()

        sys.modules["mariadb"] = MagicMock()

        self.get_database_catalog_entry_patcher = patch(
            "evadb.catalog.catalog_manager.CatalogManager.get_database_catalog_entry"
        )
        self.get_database_catalog_entry_mock = (
            self.get_database_catalog_entry_patcher.start()
        )

        self.execute_native_query_patcher = patch(
            "evadb.third_party.databases.mariadb.mariadb_handler.MariaDbHandler.execute_native_query"
        )
        self.execute_native_query_mock = self.execute_native_query_patcher.start()

        self.connect_patcher = patch(
            "evadb.third_party.databases.mariadb.mariadb_handler.MariaDbHandler.connect"
        )
        self.connect_mock = self.connect_patcher.start()

        self.disconnect_patcher = patch(
            "evadb.third_party.databases.mariadb.mariadb_handler.MariaDbHandler.disconnect"
        )
        self.disconnect_mock = self.disconnect_patcher.start()

        # set return values
        self.execute_native_query_mock.return_value = NativeQueryResponse()
        self.get_database_catalog_entry_mock.return_value = DatabaseCatalogEntry(
            name="test_data_source",
            engine="mariadb",
            params=connection_params,
            row_id=1,
        )

    def tearDown(self):
        self.get_database_catalog_entry_patcher.stop()
        self.execute_native_query_patcher.stop()
        self.connect_patcher.stop()
        self.disconnect_patcher.stop()

    def test_execute_mariadb_select_query(self):
        execute_query_fetch_all(
            self.evadb,
            """USE test_data_source {
                SELECT * FROM test_table
            }""",
        )

        self.connect_mock.assert_called_once()
        self.execute_native_query_mock.assert_called_once()
        self.get_database_catalog_entry_mock.assert_called_once()
        self.disconnect_mock.assert_called_once()

    def test_execute_mariadb_insert_query(self):
        execute_query_fetch_all(
            self.evadb,
            """USE test_data_source {
                INSERT INTO test_table (
                    name, age, comment
                ) VALUES (
                    'val', 5, 'testing'
                )
            }""",
        )
        self.connect_mock.assert_called_once()
        self.execute_native_query_mock.assert_called_once()
        self.get_database_catalog_entry_mock.assert_called_once()
        self.disconnect_mock.assert_called_once()

    def test_execute_mariadb_update_query(self):
        execute_query_fetch_all(
            self.evadb,
            """USE test_data_source {
                UPDATE test_table
                SET comment = 'update'
                WHERE age > 5
            }""",
        )

        self.connect_mock.assert_called_once()
        self.execute_native_query_mock.assert_called_once()
        self.get_database_catalog_entry_mock.assert_called_once()
        self.disconnect_mock.assert_called_once()

    def test_execute_mariadb_delete_query(self):
        execute_query_fetch_all(
            self.evadb,
            """USE test_data_source {
                DELETE FROM test_table
                WHERE age < 5
            }""",
        )

        self.connect_mock.assert_called_once()
        self.execute_native_query_mock.assert_called_once()
        self.get_database_catalog_entry_mock.assert_called_once()
        self.disconnect_mock.assert_called_once()
