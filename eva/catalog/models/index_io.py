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

from eva.catalog.catalog_type import ColumnType, Dimension, NdArrayType
from eva.catalog.models.base_model import BaseModel


class IndexIO(BaseModel):
    __tablename__ = "index_column"

    _name = Column("name", String(100))
    _type = Column("type", Enum(ColumnType), default=Enum)
    _is_nullable = Column("is_nullable", Boolean, default=False)
    _array_type = Column("array_type", Enum(NdArrayType), nullable=True)
    _array_dimensions = Column("array_dimensions", String(100))

    # Faiss index has both inputs and outputs as well. Both inputs and outputs
    # are numpy arrays.
    # Input:
    #   [Number of feature vectors, feature vector dimension]. The input needs
    #   to be float32.
    # Outputs:
    #   Distance: [Number of searched feature vectors, Top N similar feature vectors].
    #   The distance output is also float32.
    #   LogicalID: [Number of searched feature vectors. Top N similar feature vectors].
    #   The logical id output is int64.
    _is_input = Column("is_input", Boolean, default=True)

    _index_id = Column("index_id", Integer, ForeignKey("index._row_id"))
    _index = relationship("IndexMetadata", back_populates="_index_io")

    __table_args__ = (UniqueConstraint("name", "index_id"), {})

    def __init__(
        self,
        name: str,
        type: ColumnType,
        is_nullable: bool = False,
        array_type: NdArrayType = None,
        array_dimensions: List[int] = [],
        is_input: bool = True,
        index_id: int = None,
    ):
        self._name = name
        self._type = type
        self._is_nullable = is_nullable
        self._array_type = array_type
        self.array_dimensions = array_dimensions
        self._is_input = is_input
        self._index_id = index_id

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
        # Refer df_column.py:array_dimensions
        if not isinstance(value, list):
            self._array_dimensions = str(value)
        else:
            dimensions = []
            for dim in value:
                if dim == Dimension.ANYDIM:
                    dimensions.append(None)
                else:
                    dimensions.append(dim)
            self._array_dimensions = str(dimensions)

    @property
    def is_input(self):
        return self._is_input

    @property
    def index_id(self):
        return self._index_id

    @index_id.setter
    def index_id(self, value):
        self._index_id = value

    def display_format(self):
        data_type = self.type.name
        if self.type == ColumnType.NDARRAY:
            data_type = "{} {} {}".format(
                data_type, self.array_type.name, self.array_dimensions
            )

        return {"name": self.name, "data_type": data_type}

    def __str__(self):
        column_str = "\tColumn: (%s, %s, %s, %s" % (
            self._name,
            self._type.name,
            self._is_nullable,
            self._is_input,
        )
        if self.type == ColumnType.NDARRAY:
            column_str = "{} {} {}".format(
                column_str, self.array_type, self.array_dimensions
            )
        column_str += ")\n"

        return column_str

    def __eq__(self, other):
        return (
            self.id == other.id
            and self.is_input == other.is_input
            and self.is_nullable == other.is_nullable
            and self.array_type == other.array_type
            and self.array_dimensions == other.array_dimensions
            and self.name == other.name
            and self.index_id == other.index_id
            and self.type == other.type
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.id,
                self.is_input,
                self.is_nullable,
                self.array_type,
                tuple(self.array_dimensions),
                self.name,
                self.index_id,
                self.type,
            )
        )
