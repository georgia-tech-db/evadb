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
import multiprocessing as mp
from multiprocessing import Pool
from pathlib import Path

import pandas as pd

from evadb.catalog.models.table_catalog import TableCatalogEntry
from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.executor.executor_utils import ExecutorError, iter_path_regex, validate_media
from evadb.models.storage.batch import Batch
from evadb.parser.types import FileFormatType
from evadb.plan_nodes.load_data_plan import LoadDataPlan
from evadb.storage.abstract_storage_engine import AbstractStorageEngine
from evadb.storage.storage_engine import StorageEngine
from evadb.utils.errors import DatasetFileNotFoundError
from evadb.utils.generic_utils import try_to_import_cv2, try_to_import_decord
from evadb.utils.logging_manager import logger
from evadb.utils.s3_utils import download_from_s3


class LoadMultimediaExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: LoadDataPlan):
        super().__init__(db, node)
        self.media_type = self.node.file_options["file_format"]
        # check for appropriate packages
        if self.media_type == FileFormatType.IMAGE:
            try_to_import_cv2()
        elif self.media_type == FileFormatType.VIDEO:
            try_to_import_decord()
            try_to_import_cv2()

    def exec(self, *args, **kwargs):
        storage_engine = None
        table_obj = None
        try:
            video_files = []
            valid_files = []

            # If it is a s3 path, download the file to local
            if self.node.file_path.as_posix().startswith("s3:/"):
                s3_dir = Path(self.config.get_value("storage", "s3_download_dir"))
                dst_path = s3_dir / self.node.table_info.table_name
                dst_path.mkdir(parents=True, exist_ok=True)
                video_files = download_from_s3(self.node.file_path, dst_path)
            else:
                # Local Storage
                video_files = list(iter_path_regex(self.node.file_path))

            # Use parallel validation if there are many files. Otherwise, use single-thread
            # validation version.
            valid_files, invalid_files = [], []
            if len(video_files) < mp.cpu_count() * 2:
                valid_bitmap = [self._is_media_valid(path) for path in video_files]
            else:
                # TODO: move this to configuration file later.
                pool = Pool(mp.cpu_count())
                valid_bitmap = pool.map(self._is_media_valid, video_files)

            # Raise error if any file is invalid.
            if False in valid_bitmap:
                invalid_files = [
                    str(path)
                    for path, is_valid in zip(video_files, valid_bitmap)
                    if not is_valid
                ]

                invalid_files_str = "\n".join(invalid_files)
                err_msg = f"no valid file found at -- '{invalid_files_str}'."
                raise ValueError(err_msg)

            # Get valid files.
            valid_files = [
                str(path)
                for path, is_valid in zip(video_files, valid_bitmap)
                if is_valid
            ]

            if not valid_files:
                raise DatasetFileNotFoundError(
                    f"no file found at -- '{str(self.node.file_path)}'."
                )

            # Create catalog entry
            table_info = self.node.table_info
            database_name = table_info.database_name
            table_name = table_info.table_name
            # Sanity check to make sure there is no existing table with same name
            do_create = False
            table_obj = self.catalog().get_table_catalog_entry(
                table_name, database_name
            )
            if table_obj:
                msg = f"Adding to an existing table {table_name}."
                logger.info(msg)
            # Create the catalog entry
            else:
                table_obj = (
                    self.catalog().create_and_insert_multimedia_table_catalog_entry(
                        table_name, self.media_type
                    )
                )
                do_create = True

            storage_engine = StorageEngine.factory(self.db, table_obj)
            if do_create:
                storage_engine.create(table_obj)

            storage_engine.write(
                table_obj,
                Batch(pd.DataFrame({"file_path": valid_files})),
            )

        except Exception as e:
            # If we fail to obtain the storage engine or table object,
            # there is no further action to take.
            if storage_engine and table_obj:
                self._rollback_load(storage_engine, table_obj, do_create)
            err_msg = f"Load {self.media_type.name} failed: {str(e)}"
            raise ExecutorError(err_msg)
        else:
            yield Batch(
                pd.DataFrame(
                    [
                        f"Number of loaded {self.media_type.name}: {str(len(valid_files))}"
                    ]
                )
            )

    def _rollback_load(
        self,
        storage_engine: AbstractStorageEngine,
        table_obj: TableCatalogEntry,
        do_create: bool,
    ):
        if do_create:
            storage_engine.drop(table_obj)

    def _is_media_valid(
        self,
        file_path: Path,
    ):
        file_path = Path(file_path)
        if validate_media(file_path, self.media_type):
            return True
        return False
