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
import shutil
import struct
from pathlib import Path
from typing import Iterator

from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.configuration.configuration_manager import ConfigurationManager
from eva.expression.abstract_expression import AbstractExpression
from eva.models.storage.batch import Batch
from eva.storage.abstract_storage_engine import AbstractStorageEngine
from eva.utils.logging_manager import logger


class RichVideoStorageEngine(AbstractStorageEngine):

    def __init__(self):
        self.metadata = "metadata"
        self.curr_version = ConfigurationManager().get_value(
            "storage", "rich_video_engine_version"
        )

    def create(self, table: DataFrameMetadata, if_not_exists=True):
        dir_path = Path(table.file_url)
        try:
            dir_path.mkdir(parents=True)
        except FileExistsError:
            if if_not_exists:
                return True
            error = "Failed to load the video as directory \
                        already exists: {}".format(
                dir_path
            )
            logger.error(error)
            raise FileExistsError(error)
        return True

    def write(self, table: DataFrameMetadata, rows: Batch):
        try:
            df = rows.frames
            dir_path = Path(table.file_url)
            for video_file_path in df["video_file_path"]:
                video_file = Path(video_file_path)
                shutil.copy2(str(video_file), str(dir_path))
                self._create_video_metadata(dir_path, video_file.name)
        except Exception:
            error = "Current video storage engine only supports loading videos on disk."
            logger.exception(error)
            raise RuntimeError(error)
        return True

    def read(
            self,
            table: DataFrameMetadata,
            batch_mem_size: int,
            predicate: AbstractExpression = None,
            sampling_rate: int = None,
    ) -> Iterator[Batch]:
        pass

    def _create_video_metadata(self, dir_path, video_file):
        # File structure
        # <version> <length> <file_name>
        with open(dir_path / self.metadata, "ab") as f:
            # write version number
            file_path_bytes = str(video_file).encode()
            length = len(file_path_bytes)
            data = struct.pack(
                "!HH%ds" % (length,),
                self.curr_version,
                length,
                file_path_bytes,
            )
            f.write(data)
