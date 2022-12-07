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
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from eva.catalog.models.base_model import BaseModel


class UdfHistory(BaseModel):
    __tablename__ = "udf_history"

    _udf_id = Column("udf_id", Integer, ForeignKey("udf._row_id"))
    _predicate = Column("predicate", String(2048))
    _materialize_view = Column("materialize_view", String(128))

    _udf = relationship("UdfMetadata", back_populates="_history")

    _history_cols = relationship(
        "UdfHistoryColumn",
        back_populates="_history",
        # order_by='UdfHistoryColumn._arg_index',
        cascade="all, delete, delete-orphan",
    )

    def __init__(self, udf_id: int, predicate: str, materialize_view: str):
        self._udf_id = udf_id
        self._predicate = predicate
        self._materialize_view = materialize_view

    @property
    def id(self):
        return self._id

    @property
    def udf_id(self):
        return self._udf_id

    @property
    def predicate(self):
        return self._predicate

    @predicate.setter
    def predicate(self, value):
        self._predicate = value

    @property
    def materialize_view(self):
        return self._materialize_view

    def __str__(self):
        udf_history_str = "udf_history: ({}, {}, {})\n".format(
            self.udf_id, self.predicate, self.materialize_view
        )
        return udf_history_str

    def __eq__(self, other):
        return (
            self.id == other.id
            and self.udf_id == other.udf_id
            and self.predicate == other.predicate
            and self.materialize_view == other.materialize_view
        )
