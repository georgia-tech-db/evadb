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
from src.spark.session import Session
from src.catalog.models.df_metadata import DataFrameMetadata
from petastorm.etl.dataset_metadata import materialize_dataset
from src.storage.abstract_storage_engine import AbstractStorageEngine
from src.utils.logging_manager import LoggingLevel
from src.utils.logging_manager import LoggingManager

from petastorm import make_reader
from typing import Iterator

class PetastormStorageEngine(AbstractStorageEngine):

    def create(self, table: DataFrameMetadata):
        spark = Session().get_session()
        spark_context = Session().get_context()

        # Create an empty RDD
        empty_rdd = spark_context.emptyRDD()
        LoggingManager().log("URL %s" % (table.file_url), LoggingLevel.INFO)
        # Use petastorm to create dataframe
        with materialize_dataset(spark,
                                 table.file_url,
                                 table.schema.petastorm_schema):

            spark.createDataFrame(empty_rdd,
                                  table.schema.pyspark_schema) \
                .coalesce(1) \
                .write \
                .mode('overwrite') \
                .parquet(table.file_url)

    def _open(self, table):
        """
        uncertain about the functionality. Long live session for performance?
        """
        pass


    def write_row(self, table: DataFrameMetadata, row: []):
        spark = Session().get_session()

        # Convert a list of rows to RDD
        row_df = spark.createDataFrame(row,
                                       table.schema.pyspark_schema)
        row_rdd = rows_df.rdd

        # Use petastorm to appends rows
        with materialize_dataset(spark,
                                 table.file_url,
                                 table.schema.petastorm_schema):

            spark.createDataFrame(row_rdd,
                                  table.schema.pyspark_schema) \
                .coalesce(1) \
                .write \
                .mode('append') \
                .parquet(df_metadata.file_url)

    def _close(self, table):
        """
        same as _open funcition
        """
        pass

    def _read_init(self, table):
        """
        same as _open function
        """

    def read(self, table: DataFrameMetadata) -> Iterator:
        with make_reader(table.file_url) as reader:
            for frame_ind, row in enumerate(reader):
                yield row._asdict()

    def read_pos(self, table: DataFrameMetadata, pos: str):
        return None
