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
from pathlib import Path
from typing import Iterator, List

from eva.catalog.models.table_catalog import TableCatalogEntry
from eva.models.storage.batch import Batch
from eva.readers.image.opencv_image_reader import CVImageReader
from eva.storage.abstract_media_storage_engine import AbstractMediaStorageEngine
from eva.utils.logging_manager import logger


class ImageStorageEngine(AbstractMediaStorageEngine):
    def __init__(self):
        super().__init__()

    def read(self, table: TableCatalogEntry) -> Iterator[Batch]:
        for image_files in self._rdb_handler.read(self._get_metadata_table(table), 12):
            for _, (row_id, file_name) in image_files.iterrows():
                system_file_name = self._xform_file_url_to_file_name(file_name)
                image_file = Path(table.file_url) / system_file_name
                # setting batch_mem_size = 1, we need fix it
                reader = CVImageReader(str(image_file), batch_mem_size=1)
                for batch in reader.read():
                    batch.frames[table.columns[0].name] = row_id
                    batch.frames[table.columns[1].name] = str(file_name)
                    yield batch

    def clear(self, table: TableCatalogEntry, image_paths: List[Path]):
        try:
            media_metadata_table = self._get_metadata_table(table)
            for image_path in image_paths:
                dst_file_name = self._xform_file_url_to_file_name(Path(image_path))
                image_file = Path(table.file_url) / dst_file_name
                self._rdb_handler.clear(media_metadata_table)
                image_file.unlink()
        except Exception as e:
            error = f"Deleting file path {image_paths} failed with exception {e}"
            logger.exception(error)
            raise RuntimeError(error)
