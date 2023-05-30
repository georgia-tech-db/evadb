# coding=utf-8
# Copyright 2018-2023 EVA
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

from eva.database import EVADB
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError
from eva.models.storage.batch import Batch
from eva.parser.table_ref import TableInfo
from eva.plan_nodes.drop_plan import DropPlan
from eva.storage.storage_engine import StorageEngine
from eva.utils.logging_manager import logger


class DropExecutor(AbstractExecutor):
    def __init__(self, db: EVADB, node: DropPlan):
        super().__init__(db, node)

    def exec(self, *args, **kwargs):
        """Drop table executor"""

        assert len(self.node.table_infos) == 1, "Drop supports only single table"

        table_info: TableInfo = self.node.table_infos[0]

        if not self.catalog.check_table_exists(
            table_info.table_name, table_info.database_name
        ):
            err_msg = "Table: {} does not exist".format(table_info)
            if self.node.if_exists:
                logger.warn(err_msg)
                return Batch(pd.DataFrame([err_msg]))
            else:
                raise ExecutorError(err_msg)

        table_obj = self.catalog.get_table_catalog_entry(
            table_info.table_name, table_info.database_name
        )
        storage_engine = StorageEngine.factory(self.db, table_obj)

        logger.debug(f"Dropping table {table_info}")
        storage_engine.drop(table=table_obj)

        for col_obj in table_obj.columns:
            for cache in col_obj.dep_caches:
                self.catalog.drop_udf_cache_catalog_entry(cache)

        assert self.catalog.delete_table_catalog_entry(
            table_obj
        ), "Failed to drop {}".format(table_info)

        yield Batch(
            pd.DataFrame(
                {"Table Successfully dropped: {}".format(table_info.table_name)},
                index=[0],
            )
        )
