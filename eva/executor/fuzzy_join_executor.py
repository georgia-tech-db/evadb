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

from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError, apply_predicate
from eva.models.storage.batch import Batch
from eva.plan_nodes.fuzzy_join_plan import FuzzyNestedJoinPlan
from eva.utils.logging_manager import logger


class FuzzyJoinExecutor(AbstractExecutor):
    def __init__(self, node: FuzzyNestedJoinPlan):
        super().__init__(node)
        self.predicate = node.join_predicate

    def validate(self):
        pass

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        # look at either function scan executor or lateral join executor
        # children are fine
        # executes correctly
        # apply predicate
        # apply project
        # throw error


        # do a nested loop join
        
        outer = self.children[0]
        inner = self.children[1]
        try:
            for row1 in outer.exec():
                for row2 in inner.exec():
                    result_batch = Batch.join(row1, row2)
                    result_batch.reset_index()
                    result_batch = apply_predicate(result_batch, self.predicate)
                    if not result_batch.empty():
                        yield result_batch
        except Exception as e:
            logger.error(e)
            raise ExecutorError(e)

        pass

    def __call__(self, *args, **kwargs) -> Generator[Batch, None, None]:
        yield from self.exec(*args, **kwargs)
