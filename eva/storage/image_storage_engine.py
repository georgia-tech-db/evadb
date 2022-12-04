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
import io
import shutil
import struct
from pathlib import Path
from typing import Iterator

from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.configuration.configuration_manager import ConfigurationManager
from eva.models.storage.batch import Batch
from eva.readers.opencv_image_reader import CVImageReader
from eva.storage.abstract_storage_engine import AbstractStorageEngine

# from eva.utils.logging_manager import LoggingManager
# from eva.utils.logging_manager import LoggingLevel


class OpenCVImageStorageEngine(AbstractStorageEngine):
    def __init__(self):
        self.metadata = "metadata"
        self.curr_version = ConfigurationManager().get_value(
            "storage", "image_engine_version"
        )

    def create(self, table: DataFrameMetadata):
        # Create directory to store images
        dir_path = Path(table.file_url)
        try:
            dir_path.mkdir(parents=True)
        except FileExistsError:
            error = f"Failed to create, directory already exists {dir_path}"
            raise FileExistsError(error)
        self._create_metadata(dir_path)
        return True

    def write(self, table: DataFrameMetadata, image_file: Path):
        dir_path = Path(table.file_url)
        try:
            shutil.copy2(str(image_file), str(dir_path))
        except FileExistsError:
            error = "Failed to load the image as directory \
                                already exists {}".format(
                dir_path
            )
            raise FileExistsError(error)
        self._update_metadata(dir_path, image_file)

    def read(
        self,
        table: DataFrameMetadata,
        batch_size: int,
        predicate=None,
        resolution=None,
    ) -> Iterator[Batch]:

        files = self._get_file_list(table.file_url)
        reader = CVImageReader(
            files,
            batch_mem_size=batch_size,
            predicate=predicate,
            resolution=resolution,
        )
        for batch in reader.read():
            yield batch

    def _get_file_list(self, dir_path):
        metadata_file = Path(dir_path) / self.metadata
        if not metadata_file.exists():
            return
        with open(metadata_file, "rb") as f:
            (version,) = struct.unpack("!H", f.read(struct.calcsize("!H")))
            if version > self.curr_version:
                error = "Invalid metadata version {}".format(version)
                # LoggingManager().log(error, LoggingLevel.ERROR)
                raise RuntimeError(error)
            (num_files,) = struct.unpack("!H", f.read(struct.calcsize("!H")))
            for i in range(num_files):
                (length,) = struct.unpack("!H", f.read(struct.calcsize("!H")))
                path = f.read(length)
                yield Path(path.decode())

    def _get_num_files(self, dir_path):
        metadata_file = Path(dir_path) / self.metadata
        if not metadata_file.exists():
            return 0
        with open(metadata_file, "rb") as f:
            f.seek(struct.calcsize("!H"))
            (num_files,) = struct.unpack("!H", f.read(struct.calcsize("!H")))
            return num_files

    def _create_metadata(self, dir_path, overwrite=False):
        metadata_file = Path(dir_path) / self.metadata
        if metadata_file.exists():
            if not overwrite:
                print("Trying to overwrite metadata. Please set overwrite = True")
                return
        # <version> <num_files> <length> <file_name1> <length> <file_name2>
        with open(metadata_file, "wb") as f:
            # write version number
            data = struct.pack("!HH", self.curr_version, 0)
            f.write(data)

    def _update_metadata(self, dir_path, image_file):
        with open(dir_path / self.metadata, "r+b") as f:
            # increment num files
            f.seek(struct.calcsize("!H"))
            (num_files,) = struct.unpack("!H", f.read(struct.calcsize("!H")))
            num_files += 1
            f.seek(struct.calcsize("!H"))
            f.write(struct.pack("!H", num_files))
            # write version number
            f.seek(0, io.SEEK_END)
            file_path_bytes = str(image_file).encode()
            length = len(file_path_bytes)
            data = struct.pack("!H%ds" % (length,), length, file_path_bytes)
            f.write(data)
