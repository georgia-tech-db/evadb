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

from sqlalchemy import Column, String, Integer, Boolean, UniqueConstraint
from sqlalchemy.types import Enum

from src.catalog.column_type import ColumnType
from src.catalog.models.base_model import BaseModel


class DataFrameColumn(BaseModel):
    __tablename__ = 'df_column'

    _name = Column('name', String(100))
    _type = Column('type', Enum(ColumnType), default=Enum)
    _is_nullable = Column('is_nullable', Boolean, default=False)
    _array_dimensions = Column('array_dimensions', String(100))
    _metadata_id = Column('metadata_id', Integer)
    __table_args__ = (
        UniqueConstraint('name', 'metadata_id'), {}
    )

    def __init__(self,
                 name: str,
                 type: ColumnType,
                 is_nullable: bool = False,
                 array_dimensions: List[int] = [],
                 metadata_id: int = None):
        self._name = name
        self._type = type
        self._is_nullable = is_nullable
        self._array_dimensions = str(array_dimensions)
        self._metadata_id = metadata_id

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
    def metadata_id(self):
        return self._metadata_id

    @metadata_id.setter
    def metadata_id(self, value):
        self._metadata_id = value

    def __str__(self):
        column_str = "\tColumn: (%s, %s, %s, " % (self._name,
                                                  self._type.name,
                                                  self._is_nullable)

        column_str += "["
        column_str += ', '.join(['%d'] * len(self.get_array_dimensions())) \
                      % tuple(self.get_array_dimensions())
        column_str += "] "
        column_str += ")\n"

        return column_str

    @classmethod
    def get_id_from_metadata_id_and_name_in(cls, metadata_id, column_names):
        result = DataFrameColumn.query \
            .with_entities(DataFrameColumn._id) \
            .filter(DataFrameColumn._metadata_id == metadata_id,
                    DataFrameColumn._name.in_(column_names)) \
            .all()
        result = [res[0] for res in result]

        return result

    @classmethod
    def get_by_metadata_id_and_id_in(cls, id_list: List[int], metadata_id:
    int):
        """return all the columns that matches id_list and  metadata_id

        Arguments:
            id_list {List[int]} -- [metadata ids of the required columns: If 
            None return all the columns that matches the metadata_id]
            metadata_id {int} -- [metadata id of the table]

        Returns:
            List[DataFrameColumn] -- [the filtered dataframecolumns]
        """
        result = None
        if id_list is not None:
            result = DataFrameColumn.query \
                .filter(DataFrameColumn._metadata_id == metadata_id,
                        DataFrameColumn._id.in_(id_list)) \
                .all()
        else:
            result = DataFrameColumn.query \
                .filter(DataFrameColumn._metadata_id == metadata_id) \
                .all()

        return result

    @classmethod
    def create(cls, column_list):
        saved_column_list = []
        for column in column_list:
            saved_column_list.append(column_list.save())
        return saved_column_list
