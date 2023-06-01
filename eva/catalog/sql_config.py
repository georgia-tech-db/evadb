# coding=utf-8
# Copyright 2018-2023 EVA
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
from sqlalchemy import create_engine, event
from sqlalchemy.orm import session

IDENTIFIER_COLUMN = "_row_id"

CATALOG_TABLES = [
    "column_catalog",
    "table_catalog",
    "depend_column_and_udf_cache",
    "udf_cache",
    "udf_catalog",
    "depend_udf_and_udf_cache",
    "index_catalog",
    "udfio_catalog",
    "udf_cost_catalog",
    "udf_metadata_catalog",
]


class SQLConfig:
    def __init__(self, uri: str):
        """Initializes the engine and session for database operations

        Retrieves the database uri for connection from ConfigurationManager.
        """

        self.worker_uri = str(uri)
        # set echo=True to log SQL
        self.engine = create_engine(self.worker_uri, isolation_level="SERIALIZABLE")

        if self.engine.url.get_backend_name() == "sqlite":
            # enforce foreign key constraint and wal logging for sqlite
            # https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support

            def _enable_sqlite_pragma(dbapi_con, con_record):
                dbapi_con.execute("pragma foreign_keys=ON")
                dbapi_con.execute("pragma synchronous=NORMAL")
                dbapi_con.execute("pragma journal_mode=WAL")

            event.listen(self.engine, "connect", _enable_sqlite_pragma)

        # statements
        self.session = session.Session(bind=self.engine, autocommit=False)
