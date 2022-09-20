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
from eva.executor.executor_utils import apply_predicate
from eva.models.storage.batch import Batch
from eva.planner.predicate_plan import PredicatePlan


class PredicateExecutor(AbstractExecutor):
    """ """

    def __init__(self, node: PredicatePlan):
        super().__init__(node)
        self.predicate = node.predicate

    def validate(self):
        pass

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        child_executor = self.children[0]
        for batch in child_executor.exec(*args, **kwargs):
            batch = apply_predicate(batch, self.predicate)
            if not batch.empty():
                yield batch

    def __call__(self, **kwargs) -> Generator[Batch, None, None]:
        yield from self.exec(**kwargs)
