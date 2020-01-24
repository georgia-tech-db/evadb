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
from src.catalog.sql_config import sql_conn
from sqlalchemy import Column, String, Integer, Boolean
from src.catalog.df_column import DataframeColumn
from petastorm.unischema import Unischema


class Schema(sql_conn.base):

    _name = None
    _column_list = []
    _petastorm_schema = None

    def __init__(self, name: str, column_list: List[DataframeColumn]):

        self._name = name
        self._column_list = column_list
        petastorm_column_list = []
        for _column in self._column_list:
            petastorm_column = DataframeColumn.get_petastorm_column(_column)
            petastorm_column_list.append(petastorm_column)

        self._petastorm_schema = Unischema(self._schema_name,
                                           petastorm_column_list)

    def __str__(self):
        schema_str = "SCHEMA:: (" + self._schema_name + ")\n"
        for column in self._column_list:
            schema_str += str(column)

        return schema_str

    def get_petastorm_schema(self):
        return self._petastorm_schema
