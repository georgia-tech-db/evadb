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
from eva.executor.executor_utils import ExecutorError, iter_path_regex, validate_video
from eva.models.storage.batch import Batch
from eva.planner.load_data_plan import LoadDataPlan
from eva.storage.abstract_storage_engine import AbstractStorageEngine
from eva.storage.storage_engine import StorageEngine
from eva.utils.logging_manager import logger


class LoadVideoExecutor(AbstractExecutor):
    def __init__(self, node: LoadDataPlan):
        super().__init__(node)
        config = ConfigurationManager()
        self.upload_dir = Path(config.get_value("storage", "upload_dir"))

    def validate(self):
        pass

    def exec(self):
        """
        Read the input video using opencv and persist data
        using storage engine
        """

        try:
            storage_engine = StorageEngine.factory(self.node.table_metainfo)
            # ToDo: create based on if the metadata object exists in the catalog
            success = storage_engine.create(
                self.node.table_metainfo, if_not_exists=True
            )
            if not success:
                raise RuntimeError(f"StorageEngine {storage_engine} create call failed")

            valid_files = []
            invalid_files = []
            for file_path in iter_path_regex(self.node.file_path):
                if file_path.is_file():
                    # ToDo: we should validate the file before loading
                    if validate_video(file_path):
                        storage_engine.write(
                            self.node.table_metainfo,
                            Batch(pd.DataFrame([{"file_path": str(file_path)}])),
                        )
                        valid_files.append(file_path)
                    else:
                        raise ValueError(file_path)

        except RuntimeError as e:
            raise ExecutorError(str(e))
        except ValueError as e:
            self._rollback_load(storage_engine, valid_files)
            err_msg = f"Encountered invalid file while loading video {str(e)}"
            logger.error(err_msg)
            raise ExecutorError(err_msg)
        except Exception as e:
            self._rollback_load(storage_engine, valid_files)
            err_msg = f"Video Load command with unexpected error {str(e)}"
            logger.error(err_msg)
            raise ExecutorError(err_msg)
        else:
            yield Batch(
                pd.DataFrame(
                    {
                        "Number of loaded images": str(len(valid_files)),
                    },
                    index=[0],
                )
            )

    def _rollback_load(
        self,
        storage_engine: AbstractStorageEngine,
        valid_files: List[Path],
    ):
        try:
            rows = Batch(pd.DataFrame(data={"file_path": list(valid_files)}))
            storage_engine.delete(self.node.table_metainfo, rows)
        except Exception as e:
            logger.exception(
                f"Unexpected Exception {e} occured while rolling back. This is bad as the video table can be in a corrupt state. Please verify the video table {self.node.table_metainfo} for correctness."
            )
