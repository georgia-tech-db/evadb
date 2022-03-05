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
import ray

from typing import Iterator, List, Callable
from ray.data.dataset_pipeline import DatasetPipeline

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
        self.window_size = 4

    def validate(self):
        pass

    def exec(self) -> Iterator[Batch]:

        def seq_scan_ray_row(batch: Batch) -> Batch:
            # TODO The filter may be transformed into a ray filter for performance
            if not batch.empty() and self.predicate is not None:
                outcomes = self.predicate.evaluate(batch).frames
                batch = Batch(
                    batch.frames[(outcomes > 0).to_numpy()].reset_index(
                        drop=True))

            # Then do project
            if not batch.empty() and self.project_expr is not None:
                batches = [expr.evaluate(batch) for expr in self.project_expr]
                batch = Batch.merge_column_wise(batches)

            # Due to map, we need to return even when the batch is empty
            return batch

        window = []
        for batch in self.children[0].exec():
            window.append(batch)
            if len(window) >= self.window_size:
                pipe = ray.data.from_items(window).window(blocks_per_window=1)
                pipe = pipe.map(seq_scan_ray_row)
                pipe = pipe.filter(lambda b: not b.empty())
                yield from pipe.iter_rows()
                window = []
        if len(window) > 0:
                pipe = ray.data.from_items(window).window(blocks_per_window=1)
                pipe = pipe.map(seq_scan_ray_row)
                pipe = pipe.filter(lambda b: not b.empty())
                yield from pipe.iter_rows()

