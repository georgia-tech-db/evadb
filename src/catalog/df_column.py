import json
from enum import Enum
from typing import List

import numpy as np
from petastorm.codecs import NdarrayCodec
from petastorm.codecs import ScalarCodec
from petastorm.unischema import UnischemaField
from pyspark.sql.types import IntegerType, FloatType, StringType
from sqlalchemy import Column, String, Integer, Boolean

from src.catalog.sql_config import sql_conn
from src.utils.logging_manager import LoggingLevel
from src.utils.logging_manager import LoggingManager


class DataframeColumnType(Enum):
    INTEGER = 1
    FLOAT = 2
    STRING = 3
    NDARRAY = 4


class DataframeColumn(sql_conn.base):
    __tablename__ = 'df_column'

    _id = Column('id', Integer, primary_key=True)
    _name = Column('name', String)
    _type = Column('type', Enum(DataframeColumnType),
                   default=DataframeColumnType.INTEGER)
    _is_nullable = Column('is_nullable', Boolean, default=False)
    _array_dimensions = Column('array_dimensions', String, default='[]')
    _dataframe_id = Column('dataframe_id', Integer)

    def __init__(self,
                 name: str,
                 type: DataframeColumnType,
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
        return json.loads(self._array_dimensions)

    def set_array_dimensions(self, array_dimensions):
        self._array_dimensions = str(array_dimensions)

    def __str__(self):
        column_str = "\tColumn: (%s, %s, %s, " % (self._name,
                                                  self._type.name,
                                                  self._is_nullable)

        column_str += "["
        column_str += ', '.join(['%d'] * len(self._array_dimensions)) \
                      % tuple(self._array_dimensions)
        column_str += "] "
        column_str += ")\n"

        return column_str

    @staticmethod
    def get_petastorm_column(column):

        column_type = column.get_type()
        column_name = column.get_name()
        column_is_nullable = column.is_nullable()
        column_array_dimensions = column.get_array_dimensions()

        # Reference:
        # https://github.com/uber/petastorm/blob/master/petastorm/
        # tests/test_common.py

        if column_type == DataframeColumnType.INTEGER:
            petastorm_column = UnischemaField(column_name,
                                              np.int32,
                                              (),
                                              ScalarCodec(IntegerType()),
                                              column_is_nullable)
        elif column_type == DataframeColumnType.FLOAT:
            petastorm_column = UnischemaField(column_name,
                                              np.float64,
                                              (),
                                              ScalarCodec(FloatType()),
                                              column_is_nullable)
        elif column_type == DataframeColumnType.STRING:
            petastorm_column = UnischemaField(column_name,
                                              np.string_,
                                              (),
                                              ScalarCodec(StringType()),
                                              column_is_nullable)
        elif column_type == DataframeColumnType.NDARRAY:
            petastorm_column = UnischemaField(column_name,
                                              np.uint8,
                                              column_array_dimensions,
                                              NdarrayCodec(),
                                              column_is_nullable)
        else:
            LoggingManager().log("Invalid column type: " + str(column_type),
                                 LoggingLevel.ERROR)

        return petastorm_column
