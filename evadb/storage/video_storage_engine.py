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
import sys
from pathlib import Path
from typing import Iterator

from evadb.catalog.models.table_catalog import TableCatalogEntry
from evadb.database import EvaDBDatabase
from evadb.expression.abstract_expression import AbstractExpression
from evadb.models.storage.batch import Batch
from evadb.readers.decord_reader import DecordReader
from evadb.storage.abstract_media_storage_engine import AbstractMediaStorageEngine


class DecordStorageEngine(AbstractMediaStorageEngine):
    def __init__(self, db: EvaDBDatabase):
        super().__init__(db)

    def read(
        self,
        table: TableCatalogEntry,
        batch_mem_size: int,
        predicate: AbstractExpression = None,
        sampling_rate: int = None,
        sampling_type: str = None,
        read_audio: bool = False,
        read_video: bool = True,
    ) -> Iterator[Batch]:
        for video_files in self._rdb_handler.read(self._get_metadata_table(table), 12):
            for _, (row_id, video_file_name) in video_files.iterrows():
                system_file_name = self._xform_file_url_to_file_name(video_file_name)
                video_file = Path(table.file_url) / system_file_name
                # increase batch size when reading audio so that
                # the audio for the file is returned in one single batch
                if read_audio:
                    batch_mem_size = sys.maxsize
                reader = DecordReader(
                    str(video_file),
                    batch_mem_size=batch_mem_size,
                    predicate=predicate,
                    sampling_rate=sampling_rate,
                    sampling_type=sampling_type,
                    read_audio=read_audio,
                    read_video=read_video,
                )
                for batch in reader.read():
                    batch.frames[table.columns[0].name] = row_id
                    batch.frames[table.columns[1].name] = str(video_file_name)
                    yield batch
