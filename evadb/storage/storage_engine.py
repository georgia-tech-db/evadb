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
from evadb.catalog.catalog_type import TableType
from evadb.catalog.models.table_catalog import TableCatalogEntry
from evadb.database import EvaDBDatabase
from evadb.storage.abstract_storage_engine import AbstractStorageEngine
from evadb.storage.document_storage_engine import DocumentStorageEngine
from evadb.storage.image_storage_engine import ImageStorageEngine
from evadb.storage.native_storage_engine import NativeStorageEngine
from evadb.storage.pdf_storage_engine import PDFStorageEngine
from evadb.storage.sqlite_storage_engine import SQLStorageEngine
from evadb.storage.video_storage_engine import DecordStorageEngine


class StorageEngine:
    storages = None

    @classmethod
    def _lazy_initialize_storages(cls, db: EvaDBDatabase):
        if not cls.storages:
            cls.storages = {
                TableType.STRUCTURED_DATA: SQLStorageEngine,
                TableType.VIDEO_DATA: DecordStorageEngine,
                TableType.IMAGE_DATA: ImageStorageEngine,
                TableType.DOCUMENT_DATA: DocumentStorageEngine,
                TableType.PDF_DATA: PDFStorageEngine,
                TableType.NATIVE_DATA: NativeStorageEngine,
            }

    @classmethod
    def factory(
        cls, db: EvaDBDatabase, table: TableCatalogEntry
    ) -> AbstractStorageEngine:
        cls._lazy_initialize_storages(db)
        if table is None:
            raise ValueError("Expected TableCatalogEntry, got None")
        if table.table_type in cls.storages:
            return cls.storages[table.table_type](db)

        raise RuntimeError(f"Invalid table type {table.table_type}")
