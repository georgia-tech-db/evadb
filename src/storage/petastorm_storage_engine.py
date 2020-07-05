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
import os

from src.spark.session import Session
from src.catalog.models.df_metadata import DataFrameMetadata
from petastorm.etl.dataset_metadata import materialize_dataset
from src.storage.abstract_storage_engine import AbstractStorageEngine
from src.utils.logging_manager import LoggingLevel
from src.utils.logging_manager import LoggingManager
from src.configuration.configuration_manager import ConfigurationManager

from petastorm.unischema import dict_to_spark_row
from petastorm.predicates import in_set, in_lambda
from petastorm import make_reader
from typing import Iterator, Dict


class PetastormStorageEngine(AbstractStorageEngine):

    def __init__(self):
        """
        Maintain a long live spark session and context.
        """
        self._spark = Session()
        self.spark_session = self._spark.get_session()
        self.spark_context = self._spark.get_context()

    def _spark_url(self, table: DataFrameMetadata) -> str:
        """
        Generate a spark/petastorm url given a table
        """
        eva_dir = ConfigurationManager().get_value("core", "location")
        output_url = os.path.join(eva_dir, table.name)

        return output_url

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
                .coalesce(1) \
                .write \
                .mode('overwrite') \
                .parquet(self._spark_url(table))


    def write_row(self, table: DataFrameMetadata, rows: []):
        """
        Write rows into the dataframe.

        Arguments:
            rows List[Dict{key, value}]: We can formally define a dataType Row.
            keys within the Dict should be consistent with the table.schema.
        """
        def row_generator(x):
            return rows[x]

        with materialize_dataset(self.spark_session,
                                 self._spark_url(table),
                                 table.schema.petastorm_schema):

            rows_rdd = self.spark_context.parallelize(range(len(rows)))\
                .map(row_generator)\
                .map(lambda x: dict_to_spark_row(table.schema.petastorm_schema, x))

            self.spark_session.createDataFrame(rows_rdd,
                                               table.schema.pyspark_schema) \
                .coalesce(1) \
                .write \
                .mode('append') \
                .parquet(self._spark_url(table))

    def read(self, table: DataFrameMetadata) -> Iterator[Dict]:
        """
        Read the dataframe.

        Return:
            Iterator of Dict. Each Dict represents a Row.
        """
        with make_reader(self._spark_url(table)) as reader:
            for row in reader:
                yield row._asdict()

    def read_lambda(self, table: DataFrameMetadata, fields: [str], predicate_func) -> Iterator[Dict]:
        """
        Read the rows that the predicate_func returns true on the given fields.

        Argument:
            fields List[str]: A list of fields (column names) to be considered.
            predicate_func: customized function return bool
        """
        predicate = in_lambda(fields, predicate_func)
        with make_reader(self._spark_url(table), predicate = predicate) as reader:
            for row in reader:
                yield row._asdict()

    def read_pos(self, table: DataFrameMetadata, field: str, values: []) -> Iterator[Dict]:
        """
        Read the rows that matches the field's given values.

        Argument:
            field str: name of the field (column name). E.g., "id".
            values List[]: A list of values to be included.
        """
        predicate = in_set(values, field)
        with make_reader(self._spark_url(table), predicate = predicate) as reader:
            for row in reader:
                yield row._asdict()


    def _open(self, table):
        pass

    def _close(self, table):
        pass

    def _read_init(self, table):
        pass


