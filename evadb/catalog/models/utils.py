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
import contextlib
import json
from dataclasses import dataclass, field
from typing import List, Tuple

import sqlalchemy
from sqlalchemy.engine import Engine
from sqlalchemy.types import TypeDecorator
from sqlalchemy_utils import create_database, database_exists

from evadb.catalog.catalog_type import (
    ColumnType,
    NdArrayType,
    TableType,
    VectorStoreType,
)
from evadb.catalog.models.base_model import BaseModel
from evadb.catalog.sql_config import CATALOG_TABLES
from evadb.utils.logging_manager import logger


class TextPickleType(TypeDecorator):
    """Used to handle serialization and deserialization to Text
    https://stackoverflow.com/questions/1378325/python-dicts-in-sqlalchemy
    """

    impl = sqlalchemy.String(1024)

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


def init_db(engine: Engine):
    """Create database if doesn't exist and create all tables."""
    if not database_exists(engine.url):
        logger.info("Database does not exist, creating database.")
        create_database(engine.url)
    logger.info("Creating tables")
    BaseModel.metadata.create_all(bind=engine)


def truncate_catalog_tables(engine: Engine):
    """Truncate all the catalog tables"""
    # https://stackoverflow.com/questions/4763472/sqlalchemy-clear-database-content-but-dont-drop-the-schema/5003705#5003705 #noqa
    # reflect to refresh the metadata
    BaseModel.metadata.reflect(bind=engine)
    insp = sqlalchemy.inspect(engine)
    if database_exists(engine.url):
        with contextlib.closing(engine.connect()) as con:
            trans = con.begin()
            for table in reversed(BaseModel.metadata.sorted_tables):
                if insp.has_table(table.name):
                    con.execute(table.delete())
            trans.commit()


def drop_all_tables_except_catalog(engine: Engine):
    """drop all the tables except the catalog"""
    # reflect to refresh the metadata
    BaseModel.metadata.reflect(bind=engine)
    insp = sqlalchemy.inspect(engine)
    if database_exists(engine.url):
        with contextlib.closing(engine.connect()) as con:
            trans = con.begin()
            for table in reversed(BaseModel.metadata.sorted_tables):
                if table.name not in CATALOG_TABLES:
                    if insp.has_table(table.name):
                        table.drop(con)
            trans.commit()


#####
# Dataclass equivalents of catalog entries
# This is done to ensure we don't expose the sqlalchemy dependencies beyond catalog
# service. Further, sqlalchemy does not allow sharing of objects across threads.


@dataclass(unsafe_hash=True)
class UdfCacheCatalogEntry:
    """Dataclass representing an entry in the `UdfCatalog`."""

    name: str
    udf_id: int
    cache_path: str
    args: Tuple[str]
    row_id: int = None
    udf_depends: Tuple[int] = field(compare=False, default_factory=tuple)
    col_depends: Tuple[int] = field(compare=False, default_factory=tuple)


@dataclass(unsafe_hash=True)
class ColumnCatalogEntry:
    """Class decouples the ColumnCatalog from the sqlalchemy."""

    name: str
    type: ColumnType
    is_nullable: bool = False
    array_type: NdArrayType = None
    array_dimensions: Tuple[int] = field(default_factory=tuple)
    table_id: int = None
    table_name: str = None
    row_id: int = None
    dep_caches: List[UdfCacheCatalogEntry] = field(compare=False, default_factory=list)


@dataclass(unsafe_hash=True)
class TableCatalogEntry:
    """Dataclass representing an entry in the ColumnCatalog."""

    name: str
    file_url: str
    table_type: TableType
    identifier_column: str = "id"
    columns: List[ColumnCatalogEntry] = field(compare=False, default_factory=list)
    row_id: int = None


@dataclass(unsafe_hash=True)
class UdfMetadataCatalogEntry:
    """Class decouples the `UdfMetadataCatalog` from the sqlalchemy."""

    key: str
    value: str
    udf_id: int = None
    udf_name: str = None
    row_id: int = None

    def display_format(self):
        return f"{self.udf_name} - {self.key}: {self.value}"


@dataclass(unsafe_hash=True)
class UdfIOCatalogEntry:
    """Class decouples the `UdfIOCatalog` from the sqlalchemy."""

    name: str
    type: ColumnType
    is_nullable: bool = False
    array_type: NdArrayType = None
    array_dimensions: Tuple[int] = None
    is_input: bool = True
    udf_id: int = None
    udf_name: str = None
    row_id: int = None

    def display_format(self):
        data_type = self.type.name
        if self.type == ColumnType.NDARRAY:
            data_type = "{} {} {}".format(
                data_type, self.array_type.name, self.array_dimensions
            )

        return {"name": self.name, "data_type": data_type}


@dataclass(unsafe_hash=True)
class UdfCostCatalogEntry:
    """Dataclass representing an entry in the `UdfCostCatalog`."""

    name: str
    cost: float = None
    udf_id: int = None
    row_id: int = None

    def display_format(self):
        return {"udf_id": self.udf_id, "name": self.name, "cost": self.cost}


@dataclass(unsafe_hash=True)
class IndexCatalogEntry:
    """Dataclass representing an entry in the IndexCatalogEntry."""

    name: str
    save_file_path: str
    type: VectorStoreType
    row_id: int = None
    feat_column_id: int = None
    udf_signature: str = None
    feat_column: ColumnCatalogEntry = None


@dataclass(unsafe_hash=True)
class UdfCatalogEntry:
    """Dataclass representing an entry in the `UdfCatalog`.
    This is done to ensure we don't expose the sqlalchemy dependencies beyond catalog service. Further, sqlalchemy does not allow sharing of objects across threads.
    """

    name: str
    impl_file_path: str
    type: str
    checksum: str
    row_id: int = None
    args: List[UdfIOCatalogEntry] = field(compare=False, default_factory=list)
    outputs: List[UdfIOCatalogEntry] = field(compare=False, default_factory=list)
    metadata: List[UdfMetadataCatalogEntry] = field(compare=False, default_factory=list)
    dep_caches: List[UdfIOCatalogEntry] = field(compare=False, default_factory=list)

    def display_format(self):
        def _to_str(col):
            col_display = col.display_format()
            return f"{col_display['name']} {col_display['data_type']}"

        return {
            "name": self.name,
            "inputs": [_to_str(col) for col in self.args],
            "outputs": [_to_str(col) for col in self.outputs],
            "type": self.type,
            "impl": self.impl_file_path,
            "metadata": self.metadata,
        }


@dataclass(unsafe_hash=True)
class DatabaseCatalogEntry:
    """Dataclass representing an entry in the `DatabaseCatalog`.
    This is done to ensure we don't expose the sqlalchemy dependencies beyond catalog service. Further, sqlalchemy does not allow sharing of objects across threads.
    """

    name: str
    engine: str
    params: dict
    row_id: int = None

    def display_format(self):
        return {
            "name": self.name,
            "engine": self.engine,
            "params": self.params,
        }
