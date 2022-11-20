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
from typing import Generator, Iterator

from eva.catalog.catalog_type import TableType
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError
from eva.models.storage.batch import Batch
from eva.planner.storage_plan import StoragePlan
from eva.storage.storage_engine import StorageEngine


class StorageExecutor(AbstractExecutor):
    def __init__(self, node: StoragePlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self) -> Iterator[Batch]:
        storage_engine = StorageEngine.factory(self.node.video)

        if self.node.video.table_type == TableType.VIDEO_DATA:
            return storage_engine.read(
                self.node.video,
                self.node.batch_mem_size,
                predicate=self.node.predicate,
                sampling_rate=self.node.sampling_rate,
            )
        elif self.node.video.table_type == TableType.STRUCTURAL_DATA:
            return storage_engine.read(self.node.video, self.node.batch_mem_size)
        else:
            raise ExecutorError(
                f"Unsupported TableType  {self.node.video.table_type} encountered"
            )

    def __call__(self, **kwargs) -> Generator[Batch, None, None]:
        yield from self.exec()
