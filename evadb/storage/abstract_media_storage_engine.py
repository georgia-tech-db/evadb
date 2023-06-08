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
import os
import re
import shutil
from pathlib import Path

import pandas as pd

from evadb.catalog.models.table_catalog import TableCatalogEntry
from evadb.database import EvaDBDatabase
from evadb.models.storage.batch import Batch
from evadb.parser.table_ref import TableInfo
from evadb.storage.abstract_storage_engine import AbstractStorageEngine
from evadb.storage.sqlite_storage_engine import SQLStorageEngine
from evadb.utils.logging_manager import logger


class AbstractMediaStorageEngine(AbstractStorageEngine):
    def __init__(self, db: EvaDBDatabase):
        super().__init__(db)
        self._rdb_handler: SQLStorageEngine = SQLStorageEngine(db)

    def _get_metadata_table(self, table: TableCatalogEntry):
        return self.db.catalog().get_multimedia_metadata_table_catalog_entry(table)

    def _create_metadata_table(self, table: TableCatalogEntry):
        return (
            self.db.catalog().create_and_insert_multimedia_metadata_table_catalog_entry(
                table
            )
        )

    def _xform_file_url_to_file_name(self, file_url: Path) -> str:
        # Convert media_path to file name. This is done to support duplicate media_names with
        # different complete paths. Without conversion, we cannot copy files with same name but
        # different paths. Eg., a/b/my.mp4 and a/b/c/my.mp4.
        # xformed_file_name = zlib.crc32(str(file_url).encode("utf-8")) & 0xFFFFFFFF
        # return str(xformed_file_name)

        # Previous approach with hashing is commented out above. Since we now use symbolic link, the only
        # thing we need to worry about is the same file name under different directory. This motivates us
        # to just breakdown directory also as part of file name. Additionally, it does not use hashing,
        # which avoids computation overhead.
        file_path_str = str(file_url)
        file_path = re.sub(r"[^a-zA-Z0-9 \.\n]", "_", file_path_str)
        return file_path

    def create(self, table: TableCatalogEntry, if_not_exists=True):
        """
        Create the directory to store the images.
        Create a sqlite table to persist the file urls
        """
        dir_path = Path(table.file_url)
        try:
            dir_path.mkdir(parents=True)
        except FileExistsError:
            if if_not_exists:
                return True
            error = "Failed to load the image as directory \
                        already exists: {}".format(
                dir_path
            )
            logger.error(error)
            raise FileExistsError(error)

        self._rdb_handler.create(self._create_metadata_table(table))
        return True

    def drop(self, table: TableCatalogEntry):
        try:
            dir_path = Path(table.file_url)
            shutil.rmtree(str(dir_path))
            metadata_table = self._get_metadata_table(table)
            self._rdb_handler.drop(metadata_table)
            # remove the metadata table from the catalog
            self.db.catalog().delete_table_catalog_entry(metadata_table)
        except Exception as e:
            err_msg = f"Failed to drop the image table {e}"
            logger.exception(err_msg)
            raise Exception(err_msg)

    def delete(self, table: TableCatalogEntry, rows: Batch):
        try:
            media_metadata_table = self._get_metadata_table(table)
            for media_file_path in rows.file_paths():
                dst_file_name = self._xform_file_url_to_file_name(Path(media_file_path))
                image_file = Path(table.file_url) / dst_file_name
                self._rdb_handler.delete(
                    media_metadata_table,
                    where_clause={
                        media_metadata_table.identifier_column: str(media_file_path)
                    },
                )
                image_file.unlink()
        except Exception as e:
            error = f"Deleting file path {media_file_path} failed with exception {e}"
            logger.exception(error)
            raise RuntimeError(error)
        return True

    def write(self, table: TableCatalogEntry, rows: Batch):
        try:
            dir_path = Path(table.file_url)
            copied_files = []
            for media_file_path in rows.file_paths():
                media_file = Path(media_file_path)
                dst_file_name = self._xform_file_url_to_file_name(media_file)
                dst_path = dir_path / dst_file_name
                if dst_path.exists():
                    raise FileExistsError(
                        f"Duplicate File: {media_file} already exists in the table {table.name}"
                    )
                src_path = Path.cwd() / media_file
                os.symlink(src_path, dst_path)
                copied_files.append(dst_path)
            # assuming sql write is an atomic operation
            self._rdb_handler.write(
                self._get_metadata_table(table),
                Batch(pd.DataFrame({"file_url": list(rows.file_paths())})),
            )

        except Exception as e:
            # delete the copied_files
            for file in copied_files:
                logger.info(f"Rollback file {file}")
                file.unlink()
            logger.exception(str(e))
            raise RuntimeError(str(e))
        else:
            return True

    def rename(self, old_table: TableCatalogEntry, new_name: TableInfo):
        try:
            self.db.catalog().rename_table_catalog_entry(old_table, new_name)
        except Exception as e:
            raise Exception(f"Failed to rename table {new_name} with exception {e}")
