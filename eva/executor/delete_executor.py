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

import pandas as pd

from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.catalog_type import TableType
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError, apply_predicate
from eva.models.storage.batch import Batch
from eva.plan_nodes.project_plan import ProjectPlan
from eva.storage.storage_engine import StorageEngine
from eva.utils.logging_manager import logger


class DeleteExecutor(AbstractExecutor):
    """ """

    def __init__(self, node: ProjectPlan):
        super().__init__(node)
        self.predicate = node.where_clause
        self.catalog = CatalogManager()

    def validate(self):
        pass

    def exec(self, **kwargs) -> Iterator[Batch]:
        try:
            table_catalog = self.node.table_ref.table.table_obj
            storage_engine = StorageEngine.factory(table_catalog)

            if table_catalog.table_type == TableType.VIDEO_DATA:
                raise NotImplementedError("DELETE only implemented for structured data")
                # storage_engine.delete(table_catalog, del_batch)
            elif table_catalog.table_type == TableType.IMAGE_DATA:
                raise NotImplementedError("DELETE only implemented for structured data")
                # storage_engine.delete(table_catalog, del_batch)
            elif table_catalog.table_type == TableType.STRUCTURED_DATA:
                storage_engine.delete(table_catalog, self.predicate)

            yield Batch(pd.DataFrame(["Deleted rows"]))

        except Exception as e:
            logger.error(e)
            raise ExecutorError(e)
