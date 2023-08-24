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
from typing import Iterator

from evadb.catalog.catalog_type import TableType
from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.executor.executor_utils import ExecutorError
from evadb.models.storage.batch import Batch
from evadb.plan_nodes.storage_plan import StoragePlan
from evadb.storage.storage_engine import StorageEngine
from evadb.utils.logging_manager import logger


class StorageExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: StoragePlan):
        super().__init__(db, node)

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        try:
            storage_engine = StorageEngine.factory(self.db, self.node.table)

            if self.node.table.table_type == TableType.VIDEO_DATA:
                return storage_engine.read(
                    self.node.table,
                    self.node.batch_mem_size,
                    predicate=self.node.predicate,
                    sampling_rate=self.node.sampling_rate,
                    sampling_type=self.node.sampling_type,
                    read_audio=self.node.table_ref.get_audio,
                    read_video=self.node.table_ref.get_video,
                )
            elif self.node.table.table_type == TableType.IMAGE_DATA:
                return storage_engine.read(self.node.table)
            elif self.node.table.table_type == TableType.DOCUMENT_DATA:
                return storage_engine.read(self.node.table, self.node.chunk_params)
            elif self.node.table.table_type == TableType.STRUCTURED_DATA:
                return storage_engine.read(self.node.table, self.node.batch_mem_size)
            elif self.node.table.table_type == TableType.NATIVE_DATA:
                return storage_engine.read(
                    self.node.table_ref.table.database_name, self.node.table
                )
            elif self.node.table.table_type == TableType.PDF_DATA:
                return storage_engine.read(self.node.table)
            else:
                raise ExecutorError(
                    f"Unsupported TableType {self.node.table.table_type} encountered"
                )
        except Exception as e:
            logger.error(e)
            raise ExecutorError(e)
