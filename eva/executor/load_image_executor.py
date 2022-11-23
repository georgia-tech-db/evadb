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
from typing import List

import pandas as pd

from eva.configuration.configuration_manager import ConfigurationManager
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError, iter_path_regex, validate_image
from eva.models.storage.batch import Batch
from eva.planner.load_data_plan import LoadDataPlan
from eva.storage.abstract_storage_engine import AbstractStorageEngine
from eva.storage.storage_engine import StorageEngine
from eva.utils.logging_manager import logger


class LoadImageExecutor(AbstractExecutor):
    def __init__(self, node: LoadDataPlan):
        super().__init__(node)
        self.upload_dir = Path(
            ConfigurationManager().get_value("storage", "upload_dir")
        )

    def validate(self):
        pass

    def exec(self):

        try:
            storage_engine = StorageEngine.factory(self.node.table_metainfo)
            # ToDo: create based on if the metadata object exists in the catalog
            success = storage_engine.create(
                self.node.table_metainfo, if_not_exists=True
            )
            if not success:
                raise RuntimeError(f"StorageEngine {storage_engine} create call failed")

            file_count = 0
            corrupt_files = []
            for file_path in iter_path_regex(self.node.file_path):
                if file_path.is_file():
                    # we should validate the file before loading
                    if validate_image(file_path):
                        storage_engine.write(self.node.table_metainfo, file_path)
                        file_count += 1
                    else:
                        corrupt_files.append(file_path)
        except Exception as e:
            self._rollback_load(file_count, corrupt_files)
            err_msg = f"Load command with error {str(e)}"
            logger.error(err_msg)
            raise ExecutorError(err_msg)

        if corrupt_files:
            yield Batch(
                pd.DataFrame(
                    {
                        "Number of loaded images": str(file_count),
                        "Failed to load files": str(corrupt_files),
                    },
                    index=[0],
                )
            )
        else:
            yield Batch(
                pd.DataFrame(
                    {
                        "Number of loaded images": str(file_count),
                    },
                    index=[0],
                )
            )

    def _rollback_load(
        self,
        storage_engine: AbstractStorageEngine,
        file_count: int,
        corrupt_files: List[Path],
    ):
        for file_path in corrupt_files:
            storage_engine.delete(self.node.table_metainfo, file_path)
