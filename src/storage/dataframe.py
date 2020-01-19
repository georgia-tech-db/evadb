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


def load_dataframe(dataframe_url: str):

    spark = Session().get_session()
    dataframe = spark.read.load(dataframe_url)

    return dataframe


def append_rows(dataframe_url: str,
                pyspark_schema,
                petastorm_schema,
                rows):

    spark = Session().get_session()

    # Convert a list of rows to RDD
    rows_df = spark.createDataFrame(rows, schema=pyspark_schema)
    rows_rdd = rows_df.rdd

    # Use petastorm to appends rows
    with materialize_dataset(spark,
                             dataframe_url,
                             petastorm_schema):

        spark.createDataFrame(rows_rdd,
                              pyspark_schema) \
            .coalesce(1) \
            .write \
            .mode('append') \
            .parquet(dataframe_url)


def create_dataframe(dataframe_url: str,
                     pyspark_schema,
                     petastorm_schema):

    spark = Session().get_session()
    spark_context = Session().get_context()

    # Create an empty RDD
    empty_rdd = spark_context.emptyRDD()

    # Use petastorm to create dataframe
    with materialize_dataset(spark,
                             dataframe_url,
                             petastorm_schema):

        spark.createDataFrame(empty_rdd,
                              pyspark_schema) \
            .coalesce(1) \
            .write \
            .mode('overwrite') \
            .parquet(dataframe_url)
