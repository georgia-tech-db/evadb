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
from typing import Iterator, List

import numpy as np
import pandas as pd

from eva.catalog.column_type import ColumnType
from eva.catalog.models.base_model import BaseModel
from eva.catalog.models.df_column import DataFrameColumn
from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.catalog.schema_utils import SchemaUtils
from eva.catalog.sql_config import SQLConfig
from eva.models.storage.batch import Batch
from eva.storage.abstract_storage_engine import AbstractStorageEngine
from eva.utils.generic_utils import PickleSerializer, get_size
from eva.utils.logging_manager import logger

# Leveraging Dynamic schema in SQLAlchemy
# https://sparrigan.github.io/sql/sqla/2016/01/03/dynamic-tables.html


class SQLStorageEngine(AbstractStorageEngine):
    def __init__(self):
        """
        Grab the existing sql session
        """
        self._sql_session = SQLConfig().session
        self._sql_engine = SQLConfig().engine
        self._serializer = PickleSerializer

    def _dict_to_sql_row(self, dict_row: dict, columns: List[DataFrameColumn]):
        # Serialize numpy data
        for col in columns:
            if col.type == ColumnType.NDARRAY:
                dict_row[col.name] = self._serializer.serialize(dict_row[col.name])
            elif isinstance(dict_row[col.name], (np.generic,)):
                # SqlAlchemy does not consume numpy generic data types
                # convert numpy datatype to python generic datatype using tolist()
                # eg. np.int64 -> int
                # https://stackoverflow.com/a/53067954
                dict_row[col.name] = dict_row[col.name].tolist()
        return dict_row

    def _sql_row_to_dict(self, sql_row: tuple, columns: List[DataFrameColumn]):
        # Deserialize numpy data
        dict_row = {}
        for idx, col in enumerate(columns):
            if col.type == ColumnType.NDARRAY:
                dict_row[col.name] = self._serializer.deserialize(sql_row[idx])
            else:
                dict_row[col.name] = sql_row[idx]
        return dict_row

    def create(self, table: DataFrameMetadata, **kwargs):
        """
        Create an empty table in sql.
        It dynamically constructs schema in sqlaclchemy
        to create the table
        """
        attr_dict = {"__tablename__": table.name}
        sqlalchemy_schema = SchemaUtils.get_sqlalchemy_schema(table.columns)
        attr_dict.update(sqlalchemy_schema)
        # dynamic schema generation
        # https://sparrigan.github.io/sql/sqla/2016/01/03/dynamic-tables.html
        new_table = type("__placeholder_class_name", (BaseModel,), attr_dict)()
        BaseModel.metadata.tables[table.name].create(self._sql_engine)
        self._sql_session.commit()
        return new_table

    def drop(self, table: DataFrameMetadata):
        try:
            table_to_remove = BaseModel.metadata.tables[table.name]
            table_to_remove.drop()
            self._sql_session.commit()
            # In-memory metadata does not automatically sync with the database
            # therefore manually removing the table from the in-memory metadata
            # https://github.com/sqlalchemy/sqlalchemy/issues/5112
            BaseModel.metadata.remove(table_to_remove)
        except Exception as e:
            logger.exception(
                f"Failed to drop the table {table.name} with Exception {str(e)}"
            )

    def write(self, table: DataFrameMetadata, rows: Batch):
        """
        Write rows into the sql table.

        Arguments:
            table: table metadata object to write into
            rows : batch to be persisted in the storage.
        """
        new_table = BaseModel.metadata.tables[table.name]
        columns = rows.frames.keys()
        data = []
        # ToDo: validate the data type before inserting into the table
        for record in rows.frames.values:
            row_data = {col: record[idx] for idx, col in enumerate(columns)}
            data.append(self._dict_to_sql_row(row_data, table.columns))
        self._sql_engine.execute(new_table.insert(), data)
        self._sql_session.commit()

    def read(
        self,
        table: DataFrameMetadata,
        batch_mem_size: int,
    ) -> Iterator[Batch]:
        """
        Reads the table and return a batch iterator for the
        tuples.

        Argument:
            table: table metadata object of teh table to read
            batch_mem_size (int): memory size of the batch read from storage
        Return:
            Iterator of Batch read.
        """

        new_table = BaseModel.metadata.tables[table.name]
        result = self._sql_engine.execute(new_table.select())
        data_batch = []
        row_size = None
        for row in result:
            # Todo: Verfiy the order of columns in row matches the table.columns
            # ignore the first dummy (_row_id) primary column
            data_batch.append(self._sql_row_to_dict(row[1:], table.columns))
            if row_size is None:
                row_size = 0
                row_size = get_size(data_batch)
            if len(data_batch) * row_size >= batch_mem_size:
                yield Batch(pd.DataFrame(data_batch))
                data_batch = []
        if data_batch:
            yield Batch(pd.DataFrame(data_batch))
