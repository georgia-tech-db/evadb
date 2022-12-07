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

from eva.catalog.column_type import FaissIndexType, IndexMethod
from eva.catalog.models.base_model import BaseModel


class DataFrameIndex(BaseModel):
    __tablename__ = "df_index"

    _idx_name = Column("idx_name", String(100))
    _faiss_idx_type = Column("faiss_idx_type", Enum(FaissIndexType), default=None)
    _idx_method = Column("idx_method", Enum(IndexMethod), default=IndexMethod.VECTOR)

    _udf_name = Column("udf_name", String(100))

    _is_faiss_idx = Column("is_faiss_idx", Boolean, nullable=False, default=True)
    _is_res_cache = Column("is_res_cache", Boolean, nullable=False, default=True)

    _res_cache_path = Column("res_cache_path", String(255))
    _faiss_idx_path = Column("faiss_idx_path", String(255))

    _metadata_id = Column("metadata_id", Integer, ForeignKey("df_metadata.id"))

    _dataset = relationship("DataFrameMetadata", back_populates="_idx_columns")

    __table_args__ = (UniqueConstraint("idx_name", "metadata_id"), {})

    def __init__(
        self,
        idx_name: str,
        faiss_idx_type: FaissIndexType,
        idx_method: IndexMethod,
        is_faiss_idx: bool,
        is_res_cache: bool,
        res_cache_path: str,
        faiss_idx_path: str,
        metadata_id: int,
        udf_name: str
    ):
        self._idx_name = idx_name
        self._faiss_idx_type = faiss_idx_type
        self._idx_method = idx_method
        self._is_faiss_idx = is_faiss_idx
        self._is_res_cache = is_res_cache
        self._res_cache_path = res_cache_path
        self._faiss_idx_path = faiss_idx_path
        self._metadata_id = metadata_id
        self._udf_name = udf_name

    @property
    def id(self):
        return self._id

    @property
    def idx_name(self):
        return self._idx_name

    @property
    def idx_method(self):
        return self._idx_method

    @property
    def faiss_idx_type(self):
        return self._faiss_idx_type

    @property
    def is_faiss_idx(self):
        return self._is_faiss_idx

    @property
    def is_res_cache(self):
        return self._is_res_cache

    @property
    def res_cache_path(self):
        return self._res_cache_path

    @property
    def faiss_idx_path(self):
        return self._faiss_idx_path

    @property
    def udf_name(self):
        return self._udf_name

    @property
    def metadata_id(self):
        return self._metadata_id

    @metadata_id.setter
    def metadata_id(self, value):
        self._metadata_id = value

    def __str__(self):
        column_str = "Column: (idx_name: %s, metadata_id: %s, is_faiss_idx: %s, udf_name: %s)" % (
            self._idx_name,
            self._metadata_id,
            self._is_faiss_idx,
            self._udf_name
        )
        return column_str

    def __eq__(self, other):
        if other is None:
            return False
        return (
            self.id == other.id
            and self._metadata_id == other.metadata_id
            and self._faiss_idx_type == other.faiss_idx_type
            and self._udf_name == other.udf_name
            and self._idx_name == other.idx_name
            and self._faiss_idx_path == other.faiss_idx_path
        )

    def __hash__(self):
        return hash(
            (
                self._id,
                self._metadata_id,
                self._udf_name,
                self._idx_name,
                self._faiss_idx_path,
                self._res_cache_path
            )
        )
