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

from petastorm.etl.dataset_metadata import materialize_dataset


class DataFrameMetadata(object):

    _dataframe_file_url = None
    _dataframe_schema = None
    _dataframe_petastorm_schema = None
    _dataframe_pyspark_schema = None

    def __init__(self,
                 dataframe_file_url,
                 dataframe_schema
                 ):
        self._dataframe_file_url = dataframe_file_url
        self._dataframe_schema = dataframe_schema
        self._dataframe_petastorm_schema = \
            dataframe_schema.get_petastorm_schema()
        self._dataframe_pyspark_schema = \
            self._dataframe_petastorm_schema.as_spark_schema()

    def get_dataframe_file_url(self):
        return self._dataframe_file_url

    def get_dataframe_schema(self):
        return self._dataframe_schema

    def get_dataframe_petastorm_schema(self):
        return self._dataframe_petastorm_schema

    def get_dataframe_pyspark_schema(self):
        return self._dataframe_pyspark_schema


def load_dataframe(dataframe_url: str):

    spark = Session().get_session()
    dataframe = spark.read.load(dataframe_url)

    return dataframe


def append_rows(data_frame_metadata: DataFrameMetadata,
                rows):

    spark = Session().get_session()

    # Convert a list of rows to RDD
    rows_df = spark.createDataFrame(rows,
                                    schema=data_frame_metadata.get_dataframe_pyspark_schema())
    rows_rdd = rows_df.rdd

    # Use petastorm to appends rows
    with materialize_dataset(spark,
                             data_frame_metadata.get_dataframe_file_url(),
                             data_frame_metadata.get_dataframe_petastorm_schema()):

        spark.createDataFrame(rows_rdd,
                              data_frame_metadata.get_dataframe_pyspark_schema()) \
            .coalesce(1) \
            .write \
            .mode('append') \
            .parquet(data_frame_metadata.get_dataframe_file_url())


def create_dataframe(data_frame_metadata: DataFrameMetadata):

    spark = Session().get_session()
    spark_context = Session().get_context()

    # Create an empty RDD
    empty_rdd = spark_context.emptyRDD()

    # Use petastorm to create dataframe
    with materialize_dataset(spark,
                             data_frame_metadata.get_dataframe_file_url(),
                             data_frame_metadata.get_dataframe_petastorm_schema()):

        spark.createDataFrame(empty_rdd,
                              data_frame_metadata.get_dataframe_pyspark_schema()) \
            .coalesce(1) \
            .write \
            .mode('overwrite') \
            .parquet(data_frame_metadata.get_dataframe_file_url())
