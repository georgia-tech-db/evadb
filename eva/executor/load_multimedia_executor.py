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

import pandas as pd

from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.models.table_catalog import TableCatalogEntry
from eva.configuration.configuration_manager import ConfigurationManager
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError, iter_path_regex, validate_media
from eva.models.storage.batch import Batch
from eva.plan_nodes.load_data_plan import LoadDataPlan
from eva.storage.abstract_storage_engine import AbstractStorageEngine
from eva.storage.storage_engine import StorageEngine
from eva.utils.errors import DatasetFileNotFoundError
from eva.utils.logging_manager import logger
from eva.utils.s3_utils import download_from_s3


class LoadMultimediaExecutor(AbstractExecutor):
    def __init__(self, node: LoadDataPlan):
        super().__init__(node)
        self.catalog = CatalogManager()
        self.media_type = self.node.file_options["file_format"]

    def exec(self, *args, **kwargs):
        storage_engine = None
        table_obj = None
        try:
            video_files = []
            valid_files = []

            # If it is a s3 path, download the file to local
            if self.node.file_path.as_posix().startswith("s3:/"):
                s3_dir = Path(
                    ConfigurationManager().get_value("storage", "s3_download_dir")
                )
                dst_path = s3_dir / self.node.table_info.table_name
                dst_path.mkdir(parents=True, exist_ok=True)
                video_files = download_from_s3(self.node.file_path, dst_path)
            else:
                # Local Storage
                video_files = iter_path_regex(self.node.file_path)

            for file_path in video_files:
                file_path = Path(file_path)
                if validate_media(file_path, self.media_type):
                    valid_files.append(str(file_path))
                else:
                    err_msg = f"Load {self.media_type.name} failed due to invalid file {str(file_path)}"
                    logger.error(err_msg)
                    raise ValueError(file_path)

            if not valid_files:
                raise DatasetFileNotFoundError(
                    f"Load {self.media_type.name} failed due to no valid files found on path {str(self.node.file_path)}"
                )

            # Create catalog entry
            table_info = self.node.table_info
            database_name = table_info.database_name
            table_name = table_info.table_name
            # Sanity check to make sure there is no existing table with same name
            do_create = False
            table_obj = self.catalog.get_table_catalog_entry(table_name, database_name)
            if table_obj:
                msg = f"Adding to an existing table {table_name}."
                logger.info(msg)
            # Create the catalog entry
            else:
                table_obj = (
                    self.catalog.create_and_insert_multimedia_table_catalog_entry(
                        table_name, self.media_type
                    )
                )
                do_create = True

            storage_engine = StorageEngine.factory(table_obj)
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
            err_msg = f"Load {self.media_type.name} failed: encountered unexpected error {str(e)}"
            logger.error(err_msg)
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
