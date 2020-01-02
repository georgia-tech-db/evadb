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


class Schema(object):

    _column_list = []

    def __init__(self, column_list: List[Column]):
        self._column_list = column_list

    def __str__(self):
        schema_str = "SCHEMA::\n"
        for column in self._column_list:
            schema_str += str(column)

        return schema_str
