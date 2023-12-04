# coding=utf-8
# Copyright 2018-2023 EvaDB
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
from typing import Tuple

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum

from evadb.catalog.catalog_type import ColumnType, Dimension, NdArrayType
from evadb.catalog.models.base_model import BaseModel
from evadb.catalog.models.utils import FunctionIOCatalogEntry


class FunctionIOCatalog(BaseModel):
    """The `FunctionIOCatalog` catalog stores information about the input and output
    attributes of user-defined functions (Functions). It maintains the following information
    for each attribute:
    `_row_id:` an autogenerated identifier
    `_name: ` name of the input/output argument
    `_type:` the type of the argument, refer `ColumnType`
    `_rename_rules:` the rename rules for the attribute
    `_is_nullable:` which indicates whether it is nullable
    `_array_type:` the type of array, as specified in `NdArrayType` (or `None` if the attribute is a primitive type)
    `_array_dimensions:` the dimensions of the array (if `_array_type` is not `None`)
    `_function_id:` the `_row_id` of the `FunctionCatalog` entry to which the attribute belongs
    """

    __tablename__ = "functionio_catalog"

    _name = Column("name", String(100))
    _type = Column("type", Enum(ColumnType), default=Enum)
    _rename_rules = Column("rename_rules", String(500))
    _is_nullable = Column("is_nullable", Boolean, default=False)
    _array_type = Column("array_type", Enum(NdArrayType), nullable=True)
    _array_dimensions = Column("array_dimensions", String(100))
    _is_input = Column("is_input", Boolean, default=True)
    _function_id = Column(
        "function_id", Integer, ForeignKey("function_catalog._row_id")
    )

    __table_args__ = (UniqueConstraint("name", "function_id"), {})

    # Foreign key dependency with the function catalog
    _function = relationship("FunctionCatalog", back_populates="_attributes")

    def __init__(
        self,
        name: str,
        type: ColumnType,
        rename_rules: str = None,
        is_nullable: bool = False,
        array_type: NdArrayType = None,
        array_dimensions: Tuple[int] = None,
        is_input: bool = True,
        function_id: int = None,
    ):
        self._name = name
        self._type = type
        self._rename_rules = rename_rules
        self._is_nullable = is_nullable
        self._array_type = array_type
        self.array_dimensions = array_dimensions or str(())
        self._is_input = is_input
        self._function_id = function_id

    @property
    def array_dimensions(self):
        return literal_eval(self._array_dimensions)

    @array_dimensions.setter
    def array_dimensions(self, value: Tuple[int]):
        # Refer df_column.py:array_dimensions
        if not isinstance(value, tuple):
            self._array_dimensions = str(value)
        else:
            dimensions = []
            for dim in value:
                if dim == Dimension.ANYDIM:
                    dimensions.append(None)
                else:
                    dimensions.append(dim)
            self._array_dimensions = str(tuple(dimensions))

    def as_dataclass(self) -> "FunctionIOCatalogEntry":
        return FunctionIOCatalogEntry(
            row_id=self._row_id,
            name=self._name,
            type=self._type,
            rename_rules=self._rename_rules,
            is_nullable=self._is_nullable,
            array_type=self._array_type,
            array_dimensions=self.array_dimensions,
            is_input=self._is_input,
            function_id=self._function_id,
            function_name=self._function._name,
        )
