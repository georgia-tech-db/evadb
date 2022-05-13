# coding=utf-8
# Copyright 2018-2020 EVA
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

from eva.planner.create_plan import CreatePlan
from eva.executor.abstract_executor import AbstractExecutor
from eva.storage.storage_engine import StorageEngine
from eva.binder.binder_utils import (handle_if_not_exists,
                                     create_table_metadata)


class CreateExecutor(AbstractExecutor):

    def __init__(self, node: CreatePlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self):
        if not handle_if_not_exists(self.node.table_ref,
                                    self.node.if_not_exists):
            metadata = create_table_metadata(
                self.node.table_ref, self.node.column_list)
            StorageEngine.create(table=metadata)
