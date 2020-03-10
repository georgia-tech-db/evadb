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
import numpy as np
from petastorm.codecs import NdarrayCodec
from petastorm.codecs import ScalarCodec
from petastorm.unischema import Unischema
from petastorm.unischema import UnischemaField
from pyspark.sql.types import IntegerType, FloatType, StringType

from src.catalog.column_type import ColumnType
from src.utils.logging_manager import LoggingLevel
from src.utils.logging_manager import LoggingManager


class Utils(object):

    @staticmethod
    def get_petastorm_column(df_column):

        column_type = df_column.get_type()
        column_name = df_column.get_name()
        column_is_nullable = df_column.is_nullable()
        column_array_dimensions = df_column.get_array_dimensions()

        # Reference:
        # https://github.com/uber/petastorm/blob/master/petastorm/
        # tests/test_common.py

        petastorm_column = None
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
        elif column_type == ColumnType.TEXT:
            petastorm_column = UnischemaField(column_name,
                                              np.string_,
                                              (),
                                              ScalarCodec(StringType()),
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

    @staticmethod
    def get_petastorm_schema(name, column_list):
        petastorm_column_list = []
        for _column in column_list:
            petastorm_column = Utils.get_petastorm_column(_column)
            petastorm_column_list.append(petastorm_column)

        petastorm_schema = Unischema(name, petastorm_column_list)
        return petastorm_schema
