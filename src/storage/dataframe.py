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
from petastorm.unischema import dict_to_spark_row


def load_dataframe(dataframe_url: str):

    spark = Session().get_session()
    dataframe = spark.read.load(dataframe_url)

    return dataframe


def append_rows(df_metadata: DataFrameMetadata,
                rows):

    spark = Session().get_session()
    spark_context = Session().get_context()

    # Use petastorm to appends rows
    with materialize_dataset(spark,
                             df_metadata.file_url,
                             df_metadata.schema.petastorm_schema):
        # Convert a list of rows to RDD
        rows_rdd = spark_context.parallelize(rows).map(
            lambda x: dict_to_spark_row(
                df_metadata.schema.petastorm_schema, x))

        spark.createDataFrame(rows_rdd,
                              df_metadata.schema.pyspark_schema) \
            .coalesce(1) \
            .write \
            .mode('append') \
            .parquet(df_metadata.file_url)


def create_dataframe(df_metadata: DataFrameMetadata):

    spark = Session().get_session()
    spark_context = Session().get_context()

    # Create an empty RDD
    empty_rdd = spark_context.emptyRDD()
    print("url", df_metadata.file_url)
    # Use petastorm to create dataframe
    with materialize_dataset(spark,
                             df_metadata.file_url,
                             df_metadata.schema.petastorm_schema):

        spark.createDataFrame(empty_rdd,
                              df_metadata.schema.pyspark_schema) \
            .coalesce(1) \
            .write \
            .mode('overwrite') \
            .parquet(df_metadata.file_url)


def get_next_row_id(dataframe, dataframe_name: str):

    id_column_name = dataframe_name + "_id"
    row_count = dataframe.count()

    if row_count == 0:
        next_row_id = 0
    else:
        max_id = dataframe.agg({id_column_name: "max"}).collect()[0][0]
        next_row_id = max_id + 1

    return next_row_id
