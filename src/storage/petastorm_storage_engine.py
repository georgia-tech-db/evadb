# coding=utf-8
# Copyright 2018-2020 EVA
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
from pathlib import Path

from src.spark.session import Session
from src.catalog.models.df_metadata import DataFrameMetadata
from petastorm.etl.dataset_metadata import materialize_dataset
from src.storage.abstract_storage_engine import AbstractStorageEngine
from src.readers.petastorm_reader import PetastormReader
from src.models.storage.batch import Batch
from src.configuration.configuration_manager import ConfigurationManager

from petastorm.unischema import dict_to_spark_row
from petastorm.predicates import in_lambda


class PetastormStorageEngine(AbstractStorageEngine):

    def __init__(self):
        """
        Maintain a long live spark session and context.
        """
        self._spark = Session()
        self.spark_session = self._spark.get_session()
        self.spark_context = self._spark.get_context()
        self.coalesce = ConfigurationManager().get_value('pyspark', 'coalesce')

    def _spark_url(self, table: DataFrameMetadata) -> str:
        """
        Generate a spark/petastorm url given a table
        """
        return Path(table.file_url).resolve().as_uri()

    def create(self, table: DataFrameMetadata):
        """
        Create an empty dataframe in petastorm.
        """
        empty_rdd = self.spark_context.emptyRDD()

        with materialize_dataset(self.spark_session,
                                 self._spark_url(table),
                                 table.schema.petastorm_schema):

            self.spark_session.createDataFrame(empty_rdd,
                                               table.schema.pyspark_schema) \
                .coalesce(self.coalesce) \
                .write \
                .mode('overwrite') \
                .parquet(self._spark_url(table))

    def write(self, table: DataFrameMetadata, rows: Batch):
        """
        Write rows into the dataframe.

        Arguments:
            table: table metadata object to write into
            rows : batch to be persisted in the storage.
        """

        if rows.empty():
            return
        # ToDo
        # Throw an error if the row schema doesn't match the table schema

        with materialize_dataset(self.spark_session,
                                 self._spark_url(table),
                                 table.schema.petastorm_schema):

            records = rows.frames
            columns = records.keys()
            rows_rdd = self.spark_context.parallelize(records.values) \
                .map(lambda x: dict(zip(columns, x))) \
                .map(lambda x: dict_to_spark_row(table.schema.petastorm_schema,
                                                 x))
            self.spark_session.createDataFrame(rows_rdd,
                                               table.schema.pyspark_schema) \
                .coalesce(self.coalesce) \
                .write \
                .mode('append') \
                .parquet(self._spark_url(table))

    def read(self, table: DataFrameMetadata, columns: List[
            str] = None, predicate_func=None) -> Iterator[Batch]:
        """
        Reads the table and return a batch iterator for the
        tuples that passes the predicate func.

        Argument:
            table: table metadata object to write into
            columns List[str]: A list of column names to be
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
        petastorm_reader = PetastormReader(
            self._spark_url(table), predicate=predicate)
        for batch in petastorm_reader.read():
            yield batch

    def _open(self, table):
        pass

    def _close(self, table):
        pass

    def _read_init(self, table):
        pass
