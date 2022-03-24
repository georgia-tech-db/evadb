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
import shutil
import struct

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
        self.upload_path = Path(
            ConfigurationManager().get_value('storage', 'path_prefix'))
        self.curr_version = ConfigurationManager().get_value(
            'storage', 'video_engine_version')

    def create(self, table: DataFrameMetadata, video_file: Path):
        # Create directory to store video and metadata related to the video
        dir_path = Path(table.file_url)
        try:
            Path.mkdir(dir_path, parents=True)
        except FileExistsError:
            LoggingManager().log('Failed to load the video as directory \
                                already exists {}'.format(
                dir_path), LoggingLevel.ERROR)
        found = False
        # copy video from the provided path to eva datasets
        if Path(video_file).exists():
            shutil.copy2(video_file, str(dir_path))
            found = True
        # check in the upload directory
        else:
            video_path = Path(self.upload_path / video_file)
            if video_path.exists():
                shutil.copy2(str(video_path), str(dir_path))
                found = True
        if not found:
            LoggingManager().log('Failed to find the video file {}'.format(
                video_file), LoggingLevel.ERROR)
            return False
        self._create_video_metadata(dir_path, video_file.name)
        return found

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
                LoggingManager().log('Invalid metadata version {}'
                                     .format(version), LoggingLevel.ERROR)
                return False
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
