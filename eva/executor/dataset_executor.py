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
from typing import Iterator

from eva.catalog.catalog_manager import CatalogManager
from eva.executor.abstract_executor import AbstractExecutor
from eva.models.storage.batch import Batch
from eva.planner.dataset_plan import DatasetPlan
from eva.storage.storage_engine import StorageEngine, VideoStorageEngine
from eva.utils.logging_manager import logger


class DatasetExecutor(AbstractExecutor):
    """
    Expand the list of table names into contents
        node (AbstractPlan): The DatasetPlan
    """

    def __init__(self, node: DatasetPlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self) -> Iterator[Batch]:
        # We should have only two children
        assert (
            len(self.children) == 1
        ), f"DatasetExecutor expects 1 child, but {len(self.children)} found."
        child = self.children[0]
        catalog = CatalogManager()
        for batch in child.exec():
            assert (
                len(batch.columns) == 1
            ), f"DatasetExecutor expects 1-column dataframe from child, but {len(batch.columns)} found."
            for table_name in batch.frames[0]:
                metadata = catalog.get_dataset_metadata(None, table_name)
                if metadata is None:
                    logger.warn(f"Table {table_name} does not exsit.")
                elif metadata.is_dataset:
                    logger.warn(
                        f"Table {table_name} is dataset. Nested dataset is not supported."
                    )
                elif metadata.is_video:
                    return VideoStorageEngine.read(metadata, self.node.batch_mem_size)
                elif metadata.is_structured:
                    return StorageEngine.read(metadata, self.node.batch_mem_size)
