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

from enum import Enum
from typing import List

import numpy as np

from src.utils.logging_manager import LoggingManager
from src.utils.logging_manager import LoggingLevel

from pyspark.sql.types import IntegerType, FloatType

from petastorm.codecs import ScalarCodec
from petastorm.codecs import NdarrayCodec
from petastorm.unischema import Unischema, UnischemaField


class ColumnType(Enum):
    INTEGER = 1
    FLOAT = 2
    STRING = 3
    NDARRAY = 4


class Column(object):

    _name = None
    _type = 0
    _is_nullable = False
    _array_dimensions = []

    def __init__(self, name: str,
                 type: ColumnType,
                 is_nullable: bool = False,
                 array_dimensions: List[int] = []):
        self._name = name
        self._type = type
        self._is_nullable = is_nullable
        self._array_dimensions = array_dimensions

    def get_name(self):
        return self._name

    def get_type(self):
        return self._type

    def is_nullable(self):
        return self._is_nullable

    def get_array_dimensions(self):
        return self._array_dimensions

    def __str__(self):
        column_str = "\tColumn: (%s, %s, %s, " % (self._name,
                                                  self._type.name,
                                                  self._is_nullable)

        column_str += "["
        column_str += ', '.join(['%d'] * len(self._array_dimensions))\
                      % tuple(self._array_dimensions)
        column_str += "] "
        column_str += ")\n"

        return column_str


def get_petastorm_column(column):

    column_type = column.get_type()
    column_name = column.get_name()
    column_is_nullable = column.is_nullable()
    column_array_dimensions = column.get_array_dimensions()

    # Reference:
    # https://github.com/uber/petastorm/blob/master/petastorm/
    # tests/test_common.py

    if column_type == ColumnType.INTEGER:
        petastorm_column = UnischemaField(column_name,
                                          np.int32,
                                          (),
                                          ScalarCodec(IntegerType()),
                                          column_is_nullable)
    elif column_type == ColumnType.FLOAT:
        petastorm_column = UnischemaField(column_name,
                                          np.float64,
                                          (),
                                          ScalarCodec(FloatType()),
                                          column_is_nullable)
    elif column_type == ColumnType.STRING:
        petastorm_column = UnischemaField(column_name,
                                          np.unicode_,
                                          (1,),
                                          NdarrayCodec(),
                                          column_is_nullable)
    elif column_type == ColumnType.NDARRAY:
        petastorm_column = UnischemaField(column_name,
                                          np.uint8,
                                          column_array_dimensions,
                                          NdarrayCodec(),
                                          column_is_nullable)
    else:
        LoggingManager().log("Invalid column type: " + str(column_type),
                             LoggingLevel.ERROR)

    return petastorm_column


class Schema(object):

    _schema_name = None
    _column_list = []
    _petastorm_schema = None

    def __init__(self, schema_name: str, column_list: List[Column]):

        self._schema_name = schema_name
        self._column_list = column_list

        petastorm_column_list = []
        for _column in self._column_list:
            petastorm_column = get_petastorm_column(_column)
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
