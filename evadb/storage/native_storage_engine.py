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
from typing import Iterator

import pandas as pd

from evadb.catalog.models.table_catalog import TableCatalogEntry
from evadb.database import EvaDBDatabase
from evadb.models.storage.batch import Batch
from evadb.storage.abstract_storage_engine import AbstractStorageEngine
from evadb.third_party.databases.interface import get_database_handler
from evadb.utils.logging_manager import logger


class NativeStorageEngine(AbstractStorageEngine):
    def __init__(self, db: EvaDBDatabase):
        super().__init__(db)

    def create(self, table: TableCatalogEntry):
        pass

    def write(self, table: TableCatalogEntry, rows: Batch):
        pass

    def read(self, database_name: str, table: TableCatalogEntry) -> Iterator[Batch]:
        try:
            db_catalog_entry = self.db.catalog().get_database_catalog_entry(
                database_name
            )
            handler = get_database_handler(
                db_catalog_entry.engine, **db_catalog_entry.params
            )
            handler.connect()

            data_df = handler.execute_native_query(f"SELECT * FROM {table.name}").data
            yield Batch(pd.DataFrame(data_df))

        except Exception as e:
            err_msg = f"Failed to read the table {table.name} in data source {database_name} with exception {str(e)}"
            logger.exception(err_msg)
            raise Exception(err_msg)
