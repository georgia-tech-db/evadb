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


# Define a function to create a table
def create_table(uri: str, table_name: str, columns: dict):
    """
    Create a table in the database using sqlalchmey.

    Parameters:
    uri (str): the sqlalchmey uri to connect to the database
    table_name (str): The name of the table to create.
    columns (dict): A dictionary where keys are column names and values are column types.
    """
    from sqlalchemy import Column, create_engine
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

    # Create a Base class for declarative models
    Base = declarative_base()

    # Define the SQLAlchemy model class dynamically
    class CustomTable(Base):
        __tablename__ = table_name
        # Dynamically create columns based on input parameters
        for column_name, column_type in columns.items():
            locals()[column_name] = Column(column_type)

    # Create a database engine (SQLite in this example)
    engine = create_engine(uri)

    # Create the table in the database
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    session.commit()
    session.close()


class NativeStorageEngine(AbstractStorageEngine):
    def __init__(self, db: EvaDBDatabase):
        super().__init__(db)

    def write(self, table: TableCatalogEntry, rows: Batch):
        pass

    def read(self, table: TableCatalogEntry) -> Iterator[Batch]:
        try:
            db_catalog_entry = self.db.catalog().get_database_catalog_entry(
                table.database_name
            )
            with get_database_handler(
                db_catalog_entry.engine, **db_catalog_entry.params
            ) as handler:
                data_df = handler.execute_native_query(
                    f"SELECT * FROM {table.name}"
                ).data

                # Handling case-sensitive databases like SQLite can be tricky.
                # Currently, EvaDB converts all columns to lowercase, which may result
                # in issues with these databases. As we move forward, we are actively
                # working on improving this aspect within Binder. For more information,
                # please refer to https://github.com/georgia-tech-db/evadb/issues/1079.
                data_df.columns = data_df.columns.str.lower()
                yield Batch(pd.DataFrame(data_df))

        except Exception as e:
            err_msg = f"Failed to read the table {table.name} in data source {table.database_name} with exception {str(e)}"
            logger.exception(err_msg)
            raise Exception(err_msg)
