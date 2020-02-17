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

from typing import List

from src.catalog.models.df_column import DataFrameColumn
from src.catalog.schema_utils import SchemaUtils


class DataFrameSchema(object):

    def __init__(self, name: str, column_list: List[DataFrameColumn]):

        self._name = name
        self._column_list = column_list
        self._petastorm_schema = SchemaUtils.get_petastorm_schema(self._name,
                                                                  self._column_list)
        self._pyspark_schema = self._petastorm_schema.as_spark_schema()

    def __str__(self):
        schema_str = "SCHEMA:: (" + self._name + ")\n"
        for column in self._column_list:
            schema_str += str(column)
        return schema_str

    @property
    def column_list(self):
        return self._column_list

    @property
    def petastorm_schema(self):
        return self._petastorm_schema

    @property
    def pyspark_schema(self):
        return self._pyspark_schema
