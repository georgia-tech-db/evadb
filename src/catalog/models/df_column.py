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
import json
from enum import Enum
from typing import List

from sqlalchemy import Column, String, Integer, Boolean

from src.catalog.database import BaseModel
from src.catalog.column_type import ColumnType
from sqlalchemy.types import Enum


class DataFrameColumn(BaseModel):
    __tablename__ = 'df_column'

    _id = Column('id', Integer, primary_key=True)
    _name = Column('name', String(100))
    _type = Column('type', Enum(ColumnType), default=Enum)
    _is_nullable = Column('is_nullable', Boolean, default=False)
    _array_dimensions = Column('array_dimensions', String(100), default='[]')
    _metadata_id = Column('dataframe_id', Integer)

    def __init__(self,
                 name: str,
                 type: ColumnType,
                 is_nullable: bool = False,
                 array_dimensions: List[int] = []):
        self._name = name
        self._type = type
        self._is_nullable = is_nullable
        self._array_dimensions = str(array_dimensions)

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

    @classmethod
    def get_id_from_metadata_id_and_name(cls, metadata_id, name):
        result = DataFrameColumn.query\
            .with_entities(DataFrameColumn._id)\
            .filter(DataFrameColumn._metadata_id == metadata_id,
                    DataFrameColumn._name == name)\
            .one()
        return result

    @classmethod
    def get_by_metadata_id_and_id_in(cls, id_list, metadata_id):
        result = DataFrameColumn.query\
            .filter(DataFrameColumn._metadata_id == metadata_id,
                    DataFrameColumn._id.in_(id_list))\
            .all()
        return result
