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
from sqlalchemy import create_engine

from evadb.catalog.catalog_utils import generate_sqlalchemy_conn_str
from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.models.storage.batch import Batch
from evadb.plan_nodes.native_plan import SQLAlchemyPlan


class UseExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: SQLAlchemyPlan):
        super().__init__(db, node)
        self._database_name = node.database_name
        self._query_string = node.query_string

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        db_catalog_entry = self.db.catalog().get_database_catalog_entry(
            self._database_name
        )

        conn_str = generate_sqlalchemy_conn_str(
            db_catalog_entry.engine,
            db_catalog_entry.params,
        )

        engine = create_engine(conn_str)

        with engine.connect() as con:
            if "SELECT" in self._query_string or "select" in self._query_string:
                yield Batch(pd.read_sql(self._query_string, engine))
            else:
                con.execute(self._query_string)
                yield Batch(pd.DataFrame({"status": ["Ok"]}))
