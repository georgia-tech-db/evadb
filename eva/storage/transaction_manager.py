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

from filelock import SoftFileLock
from sqlalchemy import event
from sqlalchemy.orm import scoped_session, sessionmaker

from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.sql_config import SQLConfig
from eva.configuration.configuration_manager import ConfigurationManager
from eva.parser.table_ref import TableInfo
from eva.storage.storage_engine import StorageEngine


class TransactionManager:
    """Singleton class responsible for tracking the current transaction

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
            cls._instance = super(TransactionManager, cls).__new__(cls)
            cls._instance._transaction = None
        return cls._instance

    def __init__(self):
        pass

    def in_transaction(self):
        return self._transaction is not None

    def begin_transaction(self):
        if self._transaction is not None:
            raise Exception("Transaction already in progress")

        # https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
        SQLConfig().session.close()
        self._connection = SQLConfig().engine.connect()
        self._transaction = self._connection.begin()
        SQLConfig().session = scoped_session(sessionmaker(bind=self._connection))

        self.nested = SQLConfig().session.begin_nested()

        @event.listens_for(SQLConfig().session, "after_transaction_end")
        def _savepoint_on_end(session, transaction):
            if not self.nested.is_active:
                self.nested = self._connection.begin_nested()

        self._locks = []
        self._lock_names = set()  # use a set for faster lookups
        self._created_tables = []
        self._created_udfs = []

    def _acquire_lock(self, lockname):
        if not self.in_transaction():
            return
        if lockname in self._lock_names:
            return
        config = ConfigurationManager()
        lockfile = config.get_value("storage", "locks_dir") + "/" + lockname + ".lock"
        os.makedirs(os.path.dirname(lockfile), exist_ok=True)
        lock = SoftFileLock(lockfile)
        lock.acquire()

        self._locks.append(lock)
        self._lock_names.add(lockname)

    def create_table(self, table):
        if not self.in_transaction():
            return
        self._acquire_lock("table/" + table.table_name)
        self._created_tables.append(table)

    def rename_table(self, old_table_name, new_table_name):
        if not self.in_transaction():
            return
        self._acquire_lock("table/" + old_table_name)
        self._acquire_lock("table/" + new_table_name)
        for table_info in self._created_tables:
            if table_info.table_name == old_table_name:
                new_table_info = TableInfo(
                    new_table_name, table_info.schema_name, table_info.database_name
                )
                self._created_tables.remove(table_info)
                self._created_tables.append(new_table_info)
                break

    def drop_table(self, table_name):
        if not self.in_transaction():
            return
        self._acquire_lock("table/" + table_name)

    def create_udf(self, udf):
        if not self.in_transaction():
            return
        self._acquire_lock("udf/" + udf)
        self._created_udfs.append(udf)

    def drop_udf(self, udf):
        if not self.in_transaction():
            return
        self._acquire_lock("udf/" + udf)
        if udf in self._created_udfs:
            self._created_udfs.remove(udf)

    def lock_multimedia_file(self, file_name):
        if not self.in_transaction():
            return
        self._acquire_lock("multimedia/" + file_name)

    def commit_transaction(self):
        if not self.in_transaction():
            raise Exception("Transaction not in progress")
        SQLConfig().session.close()
        self._transaction.commit()
        self._connection.close()
        self._transaction = None
        SQLConfig().session = scoped_session(sessionmaker(bind=SQLConfig().engine))

        # Release all locks
        for lock in self._locks:
            while lock.is_locked:
                lock.release()

    def rollback_transaction(self):
        if not self.in_transaction():
            raise Exception("Transaction not in progress")
        SQLConfig().session.close()
        self._transaction.rollback()
        self._connection.close()
        self._transaction = None
        SQLConfig().session = scoped_session(sessionmaker(bind=SQLConfig().engine))

        # Delete all created files
        catalog_manager = CatalogManager()
        for table_info in self._created_tables:
            table_obj = catalog_manager.get_table_catalog_entry(
                table_info.table_name, table_info.database_name
            )
            if table_obj is not None:
                storage_engine = StorageEngine.factory(table_obj)
                try:
                    storage_engine.drop(table=table_obj)
                except Exception:
                    pass
                for col_obj in table_obj.columns:
                    for cache in col_obj.dep_caches:
                        try:
                            catalog_manager.drop_udf_cache_catalog_entry(cache)
                        except Exception:
                            pass
                try:
                    catalog_manager.delete_table_catalog_entry(table_obj)
                except Exception:
                    pass

        # Drop all created UDFs
        for udf in self._created_udfs:
            udf_entry = catalog_manager.get_udf_catalog_entry_by_name(udf)
            if udf_entry is not None:
                for cache in udf_entry.dep_caches:
                    catalog_manager.drop_udf_cache_catalog_entry(cache)
                catalog_manager.delete_udf_catalog_entry_by_name(udf)

        # Release all locks
        for lock in self._locks:
            while lock.is_locked:
                lock.release()
