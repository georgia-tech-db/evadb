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

from src.configuration.dictionary import DATASET_DATAFRAME_NAME

from src.storage.dataframe import load_dataframe
from src.storage.dataframe import create_dataframe

from src.catalog.schema import Column
from src.catalog.schema import ColumnType
from src.catalog.schema import Schema


def get_dataset_schema():
    column_1 = Column("dataset_id", ColumnType.INTEGER, False)
    column_2 = Column("dataset_name", ColumnType.STRING, False)

    datset_df_schema = Schema("dataset_df_schema",
                              [column_1, column_2])
    return datset_df_schema


def load_catalog_dataframes(catalog_dir_url: str,
                            catalog_dictionary):

    dataset_file_url = os.path.join(catalog_dir_url, DATASET_DATAFRAME_NAME)
    dataset_df = load_dataframe(dataset_file_url)

    dataset_df.show(10)

    dataset_df_schema = get_dataset_schema()
    dataset_df_petastorm_schema = dataset_df_schema.get_petastorm_schema()
    dataset_df_pyspark_schema = dataset_df_petastorm_schema.as_spark_schema()

    catalog_dictionary.update(
        {DATASET_DATAFRAME_NAME:
                             (dataset_df,
                              dataset_file_url,
                              dataset_df_schema,
                              dataset_df_petastorm_schema,
                              dataset_df_pyspark_schema)})


def create_catalog_dataframes(catalog_dir_url: str,
                              catalog_dictionary):

    dataset_df_schema = get_dataset_schema()
    dataset_df_petastorm_schema = dataset_df_schema.get_petastorm_schema()
    dataset_df_pyspark_schema = dataset_df_petastorm_schema.as_spark_schema()

    dataset_file_url = os.path.join(catalog_dir_url, DATASET_DATAFRAME_NAME)
    create_dataframe(dataset_file_url,
                     dataset_df_pyspark_schema,
                     dataset_df_petastorm_schema)

    dataset_df = load_dataframe(dataset_file_url)

    # dataframe name : (schema, petastorm_schema, pyspark_schema)
    catalog_dictionary.update({DATASET_DATAFRAME_NAME:
                               (dataset_df,
                                dataset_file_url,
                                dataset_df_schema,
                                dataset_df_petastorm_schema,
                                dataset_df_pyspark_schema)})
