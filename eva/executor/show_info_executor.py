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
import pandas as pd

from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.catalog_type import TableType
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError
from eva.models.storage.batch import Batch
from eva.parser.types import ShowType
from eva.plan_nodes.show_info_plan import ShowInfoPlan
from eva.utils.logging_manager import logger


class ShowInfoExecutor(AbstractExecutor):
    def __init__(self, node: ShowInfoPlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self):
        try:
            catalog_manager = CatalogManager()
            show_entries = []
            if self.node.show_type is ShowType.UDFS:
                udfs = catalog_manager.get_all_udf_catalog_entries()
                for udf in udfs:
                    show_entries.append(udf.display_format())
            elif self.node.show_type is ShowType.TABLES:
                tables = catalog_manager.get_all_table_catalog_entries()
                for table in tables:
                    if table.table_type != TableType.SYSTEM_STRUCTURED_DATA:
                        show_entries.append(table.name)
                show_entries = {"name": show_entries}
            else:
                err_msg = f"Show command does not support type {self.node.show_type}"
                logger.error(err_msg)
                raise ExecutorError(err_msg)
            yield Batch(pd.DataFrame(show_entries))
        except Exception as e:
            err_msg = f"Show executor failed with exception {str(e)}"
            logger.exception(err_msg)
            raise ExecutorError(err_msg)
