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
from dataclasses import dataclass, field
from typing import List
from sqlalchemy import Column, Enum, String
from sqlalchemy.orm import relationship

from eva.catalog.catalog_type import TableType
from eva.catalog.df_schema import DataFrameSchema
from eva.catalog.models.base_model import BaseModel
from eva.catalog.models.column_catalog import ColumnCatalogEntry
from eva.catalog.sql_config import IDENTIFIER_COLUMN


class TableCatalog(BaseModel):
    __tablename__ = "table_catalog"

    _name = Column("name", String(100), unique=True)
    _file_url = Column("file_url", String(100))
    _unique_identifier_column = Column("identifier_column", String(100))
    _table_type = Column("table_type", Enum(TableType))
    _columns = relationship(
        "ColumnCatalog",
        back_populates="_table",
        cascade="all, delete, delete-orphan",
    )

    def __init__(self, name: str, file_url: str, table_type: int, identifier_id="id"):
        self._name = name
        self._file_url = file_url
        self._schema = None
        self._unique_identifier_column = identifier_id
        self._table_type = table_type

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, column_list):
        self._schema = DataFrameSchema(self._name, column_list)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def file_url(self):
        return self._file_url

    @property
    def columns(self):
        return self._columns

    @property
    def identifier_column(self):
        return self._unique_identifier_column

    @property
    def table_type(self):
        return self._table_type

    def __eq__(self, other):
        return (
            self.id == other.id
            and self.file_url == other.file_url
            and self.schema == other.schema
            and self.identifier_column == other.identifier_column
            and self.name == other.name
            and self.table_type == other.table_type
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.id,
                self.file_url,
                self.schema,
                self.identifier_column,
                self.name,
                self.table_type,
            )
        )


@dataclass(unsafe_hash=True)
class TableCatalogEntry:
    """Class decouples the ColumnCatalog from the sqlalchemy.
    This is done to ensure we don't expose the sqlalchemy dependencies beyond catalog service. Further, sqlalchemy does not allow sharing of objects across threads.
    """

    name: str
    file_url: str
    table_type: TableType
    identifier_column: str = "id"
    id: int = None
    columns: List[ColumnCatalogEntry] = field(compare=False, default_factory=list)
    schema: DataFrameSchema = field(compare=False, default=None)
