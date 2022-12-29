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
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError
from eva.plan_nodes.rename_plan import RenamePlan
from eva.storage.storage_engine import StorageEngine
from eva.utils.logging_manager import logger


class RenameExecutor(AbstractExecutor):
    def __init__(self, node: RenamePlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self):
        """rename table executor

        Calls the catalog to modified catalog entry corresponding to the table.
        """
        try:
            obj = self.node.old_table.table.table_obj
            storage_engine = StorageEngine.factory(obj)
            storage_engine.rename(obj, self.node.new_name)
        except Exception as e:
            err = f"Rename Failed: {str(e)}"
            logger.exception(err)
            raise ExecutorError(err)
