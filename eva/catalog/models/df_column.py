# coding=utf-8
# Copyright 2018-2022 EVA
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
from ast import literal_eval
from typing import List

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum

from eva.catalog.column_type import ColumnType, Dimension, NdArrayType
from eva.catalog.models.base_model import BaseModel


class DataFrameColumn(BaseModel):
    __tablename__ = "df_column"

    _name = Column("name", String(100))
    _type = Column("type", Enum(ColumnType), default=Enum)
    _is_nullable = Column("is_nullable", Boolean, default=False)
    _array_type = Column("array_type", Enum(NdArrayType), nullable=True)
    _array_dimensions = Column("array_dimensions", String(100))
    _metadata_id = Column("metadata_id", Integer, ForeignKey("df_metadata._row_id"))

    _dataset = relationship("DataFrameMetadata", back_populates="_columns")

    __table_args__ = (UniqueConstraint("name", "metadata_id"), {})

    def __init__(
        self,
        name: str,
        type: ColumnType,
        is_nullable: bool = False,
        array_type: NdArrayType = None,
        array_dimensions: List[int] = [],
        metadata_id: int = None,
    ):
        self._name = name
        self._type = type
        self._is_nullable = is_nullable
        self._array_type = array_type
        self.array_dimensions = array_dimensions
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
    def array_type(self):
        return self._array_type

    @property
    def array_dimensions(self):
        return literal_eval(self._array_dimensions)

    @array_dimensions.setter
    def array_dimensions(self, value: List[int]):
        # This tranformation converts the ANYDIM enum to
        # None which is expected by petastorm.
        # Before adding data, petastorm verifies _is_compliant_shape
        # and any unknown dimension is expected to be None
        # https://petastorm.readthedocs.io/en/latest/_modules/petastorm/codecs.html#DataframeColumnCodec.encode
        dimensions = []
        for dim in value:
            if dim == Dimension.ANYDIM:
                dimensions.append(None)
            else:
                dimensions.append(dim)
        self._array_dimensions = str(dimensions)

    @property
    def metadata_id(self):
        return self._metadata_id

    @metadata_id.setter
    def metadata_id(self, value):
        self._metadata_id = value

    def __str__(self):
        column_str = "Column: (%s, %s, %s, " % (
            self._name,
            self._type.name,
            self._is_nullable,
        )

        column_str += "%s[" % self.array_type
        column_str += ", ".join(["%d"] * len(self.array_dimensions)) % tuple(
            self.array_dimensions
        )
        column_str += "])"

        return column_str

    def __eq__(self, other):
        return (
            self.id == other.id
            and self.metadata_id == other.metadata_id
            and self.is_nullable == other.is_nullable
            and self.array_type == other.array_type
            and self.array_dimensions == other.array_dimensions
            and self.name == other.name
            and self.type == other.type
        )

    def __hash__(self):
        return hash(
            (
                self.id,
                self.metadata_id,
                self.is_nullable,
                self.array_type,
                tuple(self.array_dimensions),
                self.name,
                self.type,
            )
        )
