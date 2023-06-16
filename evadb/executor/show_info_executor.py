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
import pandas as pd

from evadb.catalog.catalog_type import TableType
from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.models.storage.batch import Batch
from evadb.parser.types import ShowType
from evadb.plan_nodes.show_info_plan import ShowInfoPlan


class ShowInfoExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: ShowInfoPlan):
        super().__init__(db, node)

    def exec(self, *args, **kwargs):
        show_entries = []

        assert (
            self.node.show_type is ShowType.UDFS or ShowType.TABLES
        ), f"Show command does not support type {self.node.show_type}"

        if self.node.show_type is ShowType.UDFS:
            udfs = self.catalog().get_all_udf_catalog_entries()
            for udf in udfs:
                show_entries.append(udf.display_format())
        elif self.node.show_type is ShowType.TABLES:
            tables = self.catalog().get_all_table_catalog_entries()
            for table in tables:
                if table.table_type != TableType.SYSTEM_STRUCTURED_DATA:
                    show_entries.append(table.name)
            show_entries = {"name": show_entries}

        yield Batch(pd.DataFrame(show_entries))
