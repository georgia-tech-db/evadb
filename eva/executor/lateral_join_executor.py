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
from typing import Iterator
from eva.executor.executor_utils import apply_predicate, apply_project

from eva.models.storage.batch import Batch
from eva.executor.abstract_executor import AbstractExecutor
from eva.planner.lateral_join_plan import LateralJoinPlan


class LateralJoinExecutor(AbstractExecutor):

    def __init__(self, node: LateralJoinPlan):
        super().__init__(node)
        self.predicate = node.join_predicate
        self.join_project = node.join_project

    def validate(self):
        pass

    def exec(self, *args, **kwargs) -> Iterator[Batch]:

        outer = self.children[0]
        inner = self.children[1]

        for outer_batch in outer.exec():
            for result_batch in inner.exec(lateral_input=outer_batch):
                # merge
                result_batch = Batch.merge_column_wise(
                    [outer_batch, result_batch])
                result_batch = apply_predicate(result_batch, self.predicate)
                result_batch = apply_project(result_batch, self.join_project)
                if not result_batch.empty():
                    return result_batch
