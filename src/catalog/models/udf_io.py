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
from typing import List

from sqlalchemy import Column, String, Integer, Boolean, UniqueConstraint, \
    ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum

from src.catalog.column_type import ColumnType
from src.catalog.models.base_model import BaseModel


class UdfIO(BaseModel):
    __tablename__ = 'udf_column'

    _name = Column('name', String(100))
    _type = Column('type', Enum(ColumnType), default=Enum)
    _is_nullable = Column('is_nullable', Boolean, default=False)
    _array_dimensions = Column('array_dimensions', String(100))
    _is_input = Column('is_input', Boolean, default= True)
    _udf_id = Column('udf_id', Integer,
                     ForeignKey('udf.id'))
    _udf = relationship("UdfMetadata", back_populates="_cols")

    __table_args__ = (
        UniqueConstraint('name', 'udf_id'), {}
    )

    def __init__(self,
                 name: str,
                 type: ColumnType,
                 is_nullable: bool = False,
                 array_dimensions: List[int] = [],
                 is_input: bool = True,
                 udf_id: int = None):
        self._name = name
        self._type = type
        self._is_nullable = is_nullable
        self._array_dimensions = str(array_dimensions)
        self._is_input = is_input
        self._udf_id = udf_id

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def is_nullable(self):
        return self._is_nullable

    @property
    def array_dimensions(self):
        return json.loads(self._array_dimensions)

    @array_dimensions.setter
    def array_dimensions(self, value):
        self._array_dimensions = str(value)

    @property
    def is_input(self):
        return self._is_input

    @property
    def udf_id(self):
        return self._udf_id

    @udf_id.setter
    def udf_id(self, value):
        self._udf_id = value

    def __str__(self):
        column_str = "\tColumn: (%s, %s, %s, %s" % (self._name,
                                                    self._type.name,
                                                    self._is_nullable,
                                                    self._is_input)

        column_str += "["
        column_str += ', '.join(['%d'] * len(self.array_dimensions)) \
                      % tuple(self.array_dimensions)
        column_str += "] "
        column_str += ")\n"

        return column_str
