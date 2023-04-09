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
import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import scoped_session, sessionmaker

from eva.configuration.configuration_manager import ConfigurationManager

IDENTIFIER_COLUMN = "_row_id"


class SQLConfig:
    """Singleton class for configuring connection to the database.

    Attributes:
        _instance: stores the singleton instance of the class.
    """

    def __new__(cls):
        """Overrides the default __new__ method.

        Returns the existing instance or creates a new one if an instance
        does not exist.

        Returns:
            An instance of the class.
        """
        if not hasattr(cls, "_instance"):
            cls._instance = super(SQLConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initializes the engine and session for database operations

        Retrieves the database uri for connection from ConfigurationManager.
        """
        uri = ConfigurationManager().get_value("core", "catalog_database_uri")

        # to parallelize tests using pytest-xdist
        def prefix_worker_id_to_uri(uri: str):
            try:
                worker_id = os.environ["PYTEST_XDIST_WORKER"]
                base = "eva_catalog.db"
                # eva_catalog.db -> test_gw1_eva_catalog.db
                uri = uri.replace(base, "test_" + str(worker_id) + "_" + base)
            except KeyError:
                pass
            return uri

        self.worker_uri = prefix_worker_id_to_uri(str(uri))
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
        self.session = scoped_session(sessionmaker(bind=self.engine))
