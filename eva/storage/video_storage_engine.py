# coding=utf-8
# Copyright 2018-2020 EVA
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
from typing import Iterator
from pathlib import Path
import struct
import shutil

from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.storage.abstract_storage_engine import AbstractStorageEngine
from eva.readers.opencv_reader import OpenCVReader
from eva.models.storage.batch import Batch
from eva.configuration.configuration_manager import ConfigurationManager
from eva.utils.logging_manager import LoggingManager
from eva.utils.logging_manager import LoggingLevel


class VideoStorageEngine(AbstractStorageEngine):

    def __init__(self):
        self.metadata = 'metadata'
        self.curr_version = ConfigurationManager().get_value(
            'storage', 'video_engine_version')

    def create(self, table: DataFrameMetadata, video_file: Path):
        # Create directory to store video and metadata related to the video
        print('Lol')
        dir_path = Path(table.file_url)
        print(dir_path)
        print(dir_path.exists())
        try:
            dir_path.mkdir(parents=True)
            shutil.copy2(str(video_file), str(dir_path))
        except FileExistsError:
            error = 'Failed to load the video as directory \
                                already exists {}'.format(
                dir_path)
            LoggingManager().log(error, LoggingLevel.ERROR)
            raise FileExistsError(error)
        self._create_video_metadata(dir_path, video_file.name)
        return True

    def write(self, table: DataFrameMetadata, rows: Batch):
        pass

    def read(self,
             table: DataFrameMetadata,
             batch_mem_size: int,
             predicate_func=None) -> Iterator[Batch]:

        metadata_file = Path(table.file_url) / self.metadata
        video_file_name = self._get_video_file_path(metadata_file)
        video_file = Path(table.file_url) / video_file_name
        reader = OpenCVReader(str(video_file), batch_mem_size=batch_mem_size)
        for batch in reader.read():
            yield batch

    def _get_video_file_path(self, metadata_file):
        with open(metadata_file, 'rb') as f:
            (version, ) = struct.unpack('!H', f.read(struct.calcsize('!H')))
            if version > self.curr_version:
                error = 'Invalid metadata version {}'.format(version)
                LoggingManager().log(error, LoggingLevel.ERROR)
                raise RuntimeError(error)
            (length,) = struct.unpack('!H', f.read(struct.calcsize('!H')))
            path = f.read(length)
            return Path(path.decode())

    def _create_video_metadata(self, dir_path, video_file):
        # File structure
        # <version> <length> <file_name>
        with open(dir_path / self.metadata, 'wb') as f:
            # write version number
            f.write(struct.pack('!H', self.curr_version))
            file_path_bytes = str(video_file).encode()
            length = len(file_path_bytes)
            f.write(struct.pack('!H', length))
            f.write(file_path_bytes)

    def _open(self, table):
        pass

    def _close(self, table):
        pass

    def _read_init(self, table):
        pass
