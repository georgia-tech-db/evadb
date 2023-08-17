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
from threading import Lock
from weakref import WeakValueDictionary

from sqlalchemy import create_engine, event
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

from evadb.utils.generic_utils import is_postgres_uri, parse_config_yml

IDENTIFIER_COLUMN = "_row_id"

CATALOG_TABLES = [
    "column_catalog",
    "table_catalog",
    "database_catalog",
    "depend_column_and_udf_cache",
    "udf_cache",
    "udf_catalog",
    "depend_udf_and_udf_cache",
    "index_catalog",
    "udfio_catalog",
    "udf_cost_catalog",
    "udf_metadata_catalog",
]


class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """

    _instances = WeakValueDictionary()
    _lock: Lock = Lock()

    def __call__(cls, uri):
        key = (cls, uri)
        with cls._lock:
            if key not in cls._instances:
                instance = super().__call__(uri)
                cls._instances[key] = instance
        return cls._instances[key]


class SQLConfig(metaclass=SingletonMeta):
    def __init__(self, uri):
        """Initializes the engine and session for database operations

        Retrieves the database uri for connection from ConfigurationManager.
        """

        self.worker_uri = str(uri)
        # set echo=True to log SQL

        connect_args = {}
        config_obj = parse_config_yml()
        if is_postgres_uri(config_obj["core"]["catalog_database_uri"]):
            # Set the arguments for postgres backend.
            connect_args = {"connect_timeout": 1000}
            # https://www.oddbird.net/2014/06/14/sqlalchemy-postgres-autocommit/
            self.engine = create_engine(
                self.worker_uri,
                poolclass=NullPool,
                isolation_level="AUTOCOMMIT",
                connect_args=connect_args,
            )
        else:
            # Default to SQLite.
            connect_args = {"timeout": 1000}
            self.engine = create_engine(
                self.worker_uri,
                connect_args=connect_args,
            )

        if self.engine.url.get_backend_name() == "sqlite":
            # enforce foreign key constraint and wal logging for sqlite
            # https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support

            def _enable_sqlite_pragma(dbapi_con, con_record):
                dbapi_con.execute("pragma foreign_keys=ON")
                dbapi_con.execute("pragma synchronous=NORMAL")

                # disabling WAL for now, we need to fix the catalog operations.
                # Currently, there are too many connections being made, which is not an
                # optimal design. Ideally, we should implement a connection pool for
                # better management.
                # dbapi_con.execute("pragma journal_mode=WAL")
                # dbapi_con.close()

            event.listen(self.engine, "connect", _enable_sqlite_pragma)
        # statements
        self.session = scoped_session(sessionmaker(bind=self.engine))
        self.session.close()
