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

import pandas as pd

from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.catalog_type import TableType
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import apply_predicate
from eva.models.storage.batch import Batch
from eva.plan_nodes.project_plan import ProjectPlan
from eva.storage.storage_engine import StorageEngine


class DeleteExecutor(AbstractExecutor):
    """ """

    def __init__(self, node: ProjectPlan):
        super().__init__(node)
        self.predicate = node.where_clause
        self.catalog = CatalogManager()

    def exec(self, **kwargs) -> Iterator[Batch]:
        table_catalog = self.node.table_ref.table.table_obj
        storage_engine = StorageEngine.factory(table_catalog)
        del_batch = Batch()

        assert (
            table_catalog.table_type == TableType.STRUCTURED_DATA
        ), "DELETE only implemented for structured data"

        del_batch = storage_engine.read(table_catalog)
        del_batch = list(del_batch)[0]

        # Added because of inconsistency in col_alias
        # in structured data Batch project function
        original_column_names = list(del_batch.frames.columns)
        column_names = [
            f"{table_catalog.name.lower()}.{name}"
            for name in original_column_names
            if not name == "_row_id"
        ]
        column_names.insert(0, "_row_id")
        del_batch.frames.columns = column_names
        del_batch = apply_predicate(del_batch, self.predicate)

        # All the batches that need to be deleted
        del_batch.frames.columns = original_column_names
        table_needed = del_batch.frames[[f"{self.predicate.children[0].col_name}"]]
        for num in range(len(del_batch)):
            storage_engine.delete(table_catalog, table_needed.iloc[num])

        yield Batch(pd.DataFrame(["Deleted row"]))
