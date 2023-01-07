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
from typing import Iterator

from eva.catalog.models.table_catalog import TableCatalogEntry
from eva.expression.abstract_expression import AbstractExpression
from eva.models.storage.batch import Batch
from eva.readers.opencv_reader import OpenCVReader
from eva.storage.abstract_media_storage_engine import AbstractMediaStorageEngine


class OpenCVStorageEngine(AbstractMediaStorageEngine):
    def __init__(self) -> None:
        super().__init__()

    def read(
        self,
        table: TableCatalogEntry,
        batch_mem_size: int,
        predicate: AbstractExpression = None,
        sampling_rate: int = None,
    ) -> Iterator[Batch]:

        for video_files in self._rdb_handler.read(self._get_metadata_table(table), 12):
            for video_file_name in video_files.frames["file_url"]:
                system_file_name = self._xform_file_url_to_file_name(video_file_name)
                video_file = Path(table.file_url) / system_file_name
                reader = OpenCVReader(
                    str(video_file),
                    batch_mem_size=batch_mem_size,
                    predicate=predicate,
                    sampling_rate=sampling_rate,
                )
                for batch in reader.read():
                    column_name = table.columns[1].name
                    batch.frames[column_name] = str(video_file_name)
                    yield batch
