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


from src.catalog.schema import Column
from src.catalog.schema import ColumnType
from src.catalog.schema import Schema
from src.spark.session import Session

from petastorm.etl.dataset_metadata import materialize_dataset


def get_dataset_df_schema():

    column_1 = Column("dataset_id", ColumnType.INTEGER, False)
    column_2 = Column("dataset_name", ColumnType.STRING, False)

    datset_df_schema = Schema("dataset_df_schema",
                              [column_1, column_2])
    return datset_df_schema


def load_dataset_df(dataset_df_url: str):

    spark = Session().get_session()

    dataset_df = spark.read.load(dataset_df_url)

    return dataset_df


def append_row(dataset_df_url: str, dataset_name: str):

    dataset_df = load_dataset_df(dataset_df_url)
    row_count = dataset_df.count()

    if row_count == 0:
        dataset_id = 0
    else:
        max_id = dataset_df.agg({"dataset_id": "max"}).collect()[0][0]
        dataset_id = max_id + 1

    datset_df_schema = get_dataset_df_schema()
    petastorm_schema = datset_df_schema.get_petastorm_schema()
    dataset_pyspark_schema = petastorm_schema.as_spark_schema()

    spark = Session().get_session()
    Session().get_context()

    row_1 = [dataset_id, dataset_name]
    rows = [row_1]
    rows_df = spark.createDataFrame(rows, schema=dataset_pyspark_schema)
    rows_rdd = rows_df.rdd

    # Wrap dataset materialization portion.
    with materialize_dataset(spark,
                             dataset_df_url,
                             petastorm_schema):

        spark.createDataFrame(rows_rdd,
                              petastorm_schema.as_spark_schema()) \
            .coalesce(1) \
            .write \
            .mode('append') \
            .parquet(dataset_df_url)

    dataset_df = spark.read.load(dataset_df_url)
    dataset_df.show(10)


def create_datset_df(dataset_df_url: str):

    datset_df_schema = get_dataset_df_schema()    

    petastorm_schema = datset_df_schema.get_petastorm_schema()

    spark = Session().get_session()
    spark_context = Session().get_context()

    # Wrap dataset materialization portion.
    with materialize_dataset(spark,
                             dataset_df_url,
                             petastorm_schema):

        empty_rdd = spark_context.emptyRDD()

        spark.createDataFrame(empty_rdd,
                              petastorm_schema.as_spark_schema()) \
            .coalesce(1) \
            .write \
            .mode('overwrite') \
            .parquet(dataset_df_url)

