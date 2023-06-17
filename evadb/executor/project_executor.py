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

from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.executor.executor_utils import apply_project
from evadb.models.storage.batch import Batch
from evadb.plan_nodes.project_plan import ProjectPlan


class ProjectExecutor(AbstractExecutor):
    """ """

    def __init__(self, db: EvaDBDatabase, node: ProjectPlan):
        super().__init__(db, node)
        self.target_list = node.target_list

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        child_executor = self.children[0]
        for batch in child_executor.exec(**kwargs):
            batch = apply_project(batch, self.target_list, self.catalog())

            if not batch.empty():
                yield batch
