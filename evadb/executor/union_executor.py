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
from evadb.models.storage.batch import Batch
from evadb.plan_nodes.union_plan import UnionPlan


class UnionExecutor(AbstractExecutor):
    """
    Merge the seq scan queries
    Arguments:
        node (AbstractPlan): The UnionPlan

    """

    def __init__(self, db: EvaDBDatabase, node: UnionPlan):
        super().__init__(db, node)

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        assert self.node.all is True, "Only UNION ALL is supported now."

        # We should have only two children
        for child in self.children:
            for batch in child.exec():
                yield batch
