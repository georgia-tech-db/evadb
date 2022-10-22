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
import shutil
from pathlib import Path
from typing import Iterator, List

from petastorm.etl.dataset_metadata import materialize_dataset
from petastorm.predicates import in_lambda
from petastorm.unischema import dict_to_spark_row

from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.catalog.sql_config import SQLConfig
from eva.configuration.configuration_manager import ConfigurationManager
from eva.models.storage.batch import Batch
from eva.readers.petastorm_reader import PetastormReader
from eva.storage.abstract_storage_engine import AbstractStorageEngine
from eva.utils.logging_manager import logger
from eva.catalog.models.base_model import BaseModel
from eva.catalog.schema_utils import SchemaUtils

# Leveraging Dynamic schema in SQLAlchemy
# https://sparrigan.github.io/sql/sqla/2016/01/03/dynamic-tables.html


class SQLStorageEngine(AbstractStorageEngine):
    def __init__(self):
        """
        Grab the existing sql session
        """
        self._sql_session = SQLConfig().session

    def create(self, table: DataFrameMetadata, **kwargs):
        """
        Create an empty table in sql.
        """
        attr_dict = {"__tablename__": table.name}
        sqlalchemy_schema = SchemaUtils.get_sqlalchemy_schema(table.columns)
        attr_dict.update(sqlalchemy_schema)
        new_table = type("new_table", (BaseModel,), attr_dict)
        BaseModel.metadata.create_table(tables=[new_table.__table__])

    def drop(self, table: DataFrameMetadata):
        dir_path = self._spark_url(table)
        try:
            shutil.rmtree(str(dir_path))
        except Exception as e:
            logger.exception(f"Failed to drop the video table {e}")

    def write(self, table: DataFrameMetadata, rows: Batch):
        """
        Write rows into the sql table.

        Arguments:
            table: table metadata object to write into
            rows : batch to be persisted in the storage.
        """
        attr_dict = {"__tablename__": table.name}
        sqlalchemy_schema = SchemaUtils.get_sqlalchemy_schema(table.columns)
        attr_dict.update(sqlalchemy_schema)
        new_table = type("new_table", (BaseModel,), attr_dict)
        
        columns = rows.frames.keys() 
        data = []
        for record in rows.frames.values:
            row_data = { col : record[col] for col in columns}
            data.append(row_data)
        self._sql_session.bulk_insert_mappings(new_table, data)
        self._sql_session.commit()

    def read(
        self,
        table: DataFrameMetadata,
        batch_mem_size: int,
        columns: List[str] = None,
        predicate_func=None,
    ) -> Iterator[Batch]:
        """
        Reads the table and return a batch iterator for the
        tuples that passes the predicate func.

        Argument:
            table: table metadata object to write into
            batch_mem_size (int): memory size of the batch read from storage
            columns (List[str]): A list of column names to be
                considered in predicate_func
            predicate_func: customized predicate function returns bool

        Return:
            Iterator of Batch read.
        """
        predicate = None
        if predicate_func and columns:
            predicate = in_lambda(columns, predicate_func)

        # ToDo: Handle the sharding logic. We might have to maintain a
        # context for deciding which shard to read
        reader = PetastormReader(
            self._spark_url(table),
            batch_mem_size=batch_mem_size,
            predicate=predicate,
        )
        for batch in reader.read():
            yield batch
