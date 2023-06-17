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
from pathlib import Path
from typing import Iterator

from evadb.catalog.models.table_catalog import TableCatalogEntry
from evadb.database import EvaDBDatabase
from evadb.models.storage.batch import Batch
from evadb.readers.document.document_reader import DocumentReader
from evadb.storage.abstract_media_storage_engine import AbstractMediaStorageEngine


class DocumentStorageEngine(AbstractMediaStorageEngine):
    def __init__(self, db: EvaDBDatabase):
        super().__init__(db)

    def read(self, table: TableCatalogEntry, chunk_params: dict) -> Iterator[Batch]:
        for doc_files in self._rdb_handler.read(self._get_metadata_table(table), 12):
            for _, (row_id, file_name) in doc_files.iterrows():
                system_file_name = self._xform_file_url_to_file_name(file_name)
                doc_file = Path(table.file_url) / system_file_name
                # setting batch_mem_size = 1, we need fix it
                reader = DocumentReader(
                    str(doc_file), batch_mem_size=1, chunk_params=chunk_params
                )
                for batch in reader.read():
                    batch.frames[table.columns[0].name] = row_id
                    batch.frames[table.columns[1].name] = str(file_name)
                    yield batch
