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
from dataclasses import dataclass

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum

from eva.catalog.catalog_type import IndexType
from eva.catalog.models.base_model import BaseModel
from eva.catalog.models.column_catalog import ColumnCatalogEntry


class IndexCatalog(BaseModel):
    """The `IndexCatalogEntry` catalog stores information about all the indexes in the system.
    `_row_id:` an autogenerated unique identifier.
    `_name:` the name of the index.
    `_save_file_path:` the path to the index file on disk
    `_type:` the type of the index (refer to `IndexType`)
    `_feat_column_id:` the `_row_id` of the `ColumnCatalog` entry for the column on which the index is built.
    `_udf_signature:` if the index is created by running udf expression on input column, this will store
                      the udf signature of the used udf. Otherwise, this field is None.
    """

    __tablename__ = "index_catalog"

    _name = Column("name", String(100), unique=True)
    _save_file_path = Column("save_file_path", String(128))
    _type = Column("type", Enum(IndexType), default=Enum)
    _feat_column_id = Column("column_id", Integer, ForeignKey("column_catalog._row_id", ondelete="CASCADE"))
    _udf_signature = Column("udf", String, default=None)

    _feat_column = relationship(
        "ColumnCatalog",
        back_populates="_index_column",
    )

    def __init__(
        self,
        name: str,
        save_file_path: str,
        type: IndexType,
        feat_column_id: int = None,
        udf_signature: str = None,
    ):
        self._name = name
        self._save_file_path = save_file_path
        self._type = type
        self._feat_column_id = feat_column_id
        self._udf_signature = udf_signature

    def as_dataclass(self) -> "IndexCatalogEntry":
        feat_column = self._feat_column.as_dataclass() if self._feat_column else None
        return IndexCatalogEntry(
            row_id=self._row_id,
            name=self._name,
            save_file_path=self._save_file_path,
            type=self._type,
            feat_column_id=self._feat_column_id,
            udf_signature=self._udf_signature,
            feat_column=feat_column,
        )


@dataclass(unsafe_hash=True)
class IndexCatalogEntry:
    """Dataclass representing an entry in the IndexCatalogEntry.
    This is done to ensure we don't expose the sqlalchemy dependencies beyond catalog service. Further, sqlalchemy does not allow sharing of objects across threads.
    """

    name: str
    save_file_path: str
    type: IndexType
    row_id: int = None
    feat_column_id: int = None
    udf_signature: str = None
    feat_column: ColumnCatalogEntry = None
