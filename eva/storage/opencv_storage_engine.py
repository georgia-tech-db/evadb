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
import os
import shutil
import struct
from pathlib import Path
from typing import Iterator

from sqlalchemy import Column
from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.catalog_type import TableType

from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.catalog.sql_config import SQLConfig
from eva.configuration.configuration_manager import ConfigurationManager
from eva.expression.abstract_expression import AbstractExpression
from eva.models.storage.batch import Batch
from eva.readers.opencv_reader import OpenCVReader
from eva.storage.abstract_storage_engine import AbstractStorageEngine
from eva.storage.sqlite_storage_engine import SQLStorageEngine
from eva.utils.logging_manager import logger


class OpenCVStorageEngine(AbstractStorageEngine):
    def __init__(self):
        self._rdb_handler: SQLStorageEngine = SQLStorageEngine()

    @staticmethod
    def _get_metadata_table(table: DataFrameMetadata):
        return CatalogManager().get_video_metadata_table(table)

    def create(self, table: DataFrameMetadata, if_not_exists=True):
        """
        Create the directory to store the video.
        Create a sqlite table to persist the file urls
        """
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

        self._rdb_handler.create(self._get_metadata_table(table))
        return True

    def drop(self, table: DataFrameMetadata):
        dir_path = Path(table.file_url)
        try:
            shutil.rmtree(str(dir_path))
            self._rdb_handler.drop(self._get_metadata_table(table))
        except Exception as e:
            logger.exception(f"Failed to drop the video table {e}")

    def delete(self, table: DataFrameMetadata, rows: Batch):
        try:
            video_metadata_table = self._get_metadata_table(table)
            for video_file_path in rows.file_paths():
                video_file = Path(table.file_url) / video_file_path
                video_file.unlink()
                self._rdb_handler.delete(
                    video_metadata_table,
                    where_clause={video_metadata_table.identifier_id: video_file_path},
                )
        except Exception:
            error = f"Deleting file path {video_file_path} failed"
            logger.exception(error)
            raise RuntimeError(error)
        return True

    def write(self, table: DataFrameMetadata, rows: Batch):
        try:
            dir_path = Path(table.file_url)
            for video_file_path in rows.file_paths():
                video_file = Path(video_file_path)
                shutil.copy2(str(video_file), str(dir_path))
                self._rdb_handler.write(
                    self._get_metadata_table(table, video_file.name)
                )
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

        for video_file_name in self._rdb_handler.read(
            self._get_metadata_table(table), 1
        ):
            video_file = Path(table.file_url) / video_file_name
            reader = OpenCVReader(
                str(video_file),
                batch_mem_size=batch_mem_size,
                predicate=predicate,
                sampling_rate=sampling_rate,
            )
            for batch in reader.read():
                column_name = table.columns[0].name
                batch.frames[column_name] = str(video_file_name)
                yield batch

    def _open(self, table):
        pass

    def _close(self, table):
        pass

    def _read_init(self, table):
        pass
