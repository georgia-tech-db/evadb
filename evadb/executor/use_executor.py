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

from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.executor.executor_utils import ExecutorError
from evadb.models.storage.batch import Batch
from evadb.parser.use_statement import UseStatement
from evadb.third_party.databases.interface import get_database_handler


class UseExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: UseStatement):
        super().__init__(db, node)
        self._database_name = node.database_name
        self._query_string = node.query_string

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        db_catalog_entry = self.db.catalog().get_database_catalog_entry(
            self._database_name
        )

        if db_catalog_entry is None:
            raise ExecutorError(
                f"{self._database_name} data source does not exist. Use CREATE DATABASE to add a new data source."
            )

        with get_database_handler(
            db_catalog_entry.engine, **db_catalog_entry.params
        ) as handler:
            resp = handler.execute_native_query(self._query_string)

        if resp and resp.error is None:
            yield Batch(resp.data)
        else:
            raise ExecutorError(resp.error)
