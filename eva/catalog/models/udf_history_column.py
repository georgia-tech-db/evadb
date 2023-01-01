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
from typing import List

from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from eva.catalog.models.base_model import BaseModel


class UdfHistoryColumn(BaseModel):
    __tablename__ = "udf_history_column"

    _udf_history_id = Column(
        "udf_history_id", Integer, ForeignKey("udf_history._row_id")
    )
    _arg = Column("arg", Integer, ForeignKey("df_column._row_id"))
    _arg_index = Column("arg_index", Integer)

    _history = relationship("UdfHistory", back_populates="_history_cols")

    _col = relationship("DataFrameColumn", back_populates="_udf_history_arg")

    __table_args__ = (UniqueConstraint("udf_history_id", "arg_index"), {})

    def __init__(self, udf_history_id: int, arg: int, arg_index: int):
        self._udf_history_id = udf_history_id
        self._arg = arg
        self._arg_index = arg_index

    @property
    def id(self):
        return self._id

    @property
    def udf_history_id(self):
        return self._udf_history_id

    @property
    def arg(self):
        return self._arg

    @property
    def arg_index(self):
        return self._arg_index

    def __str__(self):
        history_column_str = "udf_history_col:({}, {}, {})\n".format(
            self.udf_history_id, self.arg, self.arg_index
        )
        return history_column_str

    def __eq__(self, other):
        return (
            self.id == other.id
            and self.udf_history_id == other.udf_history_id
            and self.arg == other.arg
            and self.arg_index == other.arg_index
        )
