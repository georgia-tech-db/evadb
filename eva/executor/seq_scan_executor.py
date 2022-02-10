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

from eva.models.storage.batch import Batch
from eva.executor.abstract_executor import AbstractExecutor
from eva.planner.seq_scan_plan import SeqScanPlan


class SequentialScanExecutor(AbstractExecutor):
    """
    Applies predicates to filter the frames which satisfy the condition
    Arguments:
        node (AbstractPlan): The SequentialScanPlan

    """

    def __init__(self, node: SeqScanPlan):
        super().__init__(node)
        self.predicate = node.predicate
        self.project_expr = node.columns

    def validate(self):
        pass

    def exec(self, *args, **kwargs) -> Iterator[Batch]:

        child_executor = self.children[0]
        for batch in child_executor.exec():
            # We do the predicate first
            if not batch.empty() and self.predicate is not None:
                outcomes = self.predicate.evaluate(batch).frames
                batch = Batch(
                    batch.frames[(outcomes > 0).to_numpy()].reset_index(
                        drop=True))

            # Then do project
            if not batch.empty() and self.project_expr is not None:
                batches = [expr.evaluate(batch) for expr in self.project_expr]
                batch = Batch.merge_column_wise(batches)

            if not batch.empty():
                yield batch
