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
from typing import Iterator

from eva.executor.abstract_executor import AbstractExecutor
from eva.models.storage.batch import Batch
from eva.plan_nodes.extract_object_plan import ExtractObjectPlan


class ExtractObjectExecutor(AbstractExecutor):
    """ """

    def __init__(self, node: ExtractObjectPlan):
        super().__init__(node)
        self.detector = node.detector
        self.tracker = node.tracker

    def exec(self) -> Iterator[Batch]:
        child_executor = self.children[0]
        for batch in child_executor.exec():
            # run detector
            objects = self.detector.evaluate(batch)

            # run tracker
            intermediate_batch = Batch.merge_column_wise([batch, objects])
            results = self.tracker.evaluate(intermediate_batch)

            # merge batch and tracker outputs and yield
            outcomes = Batch.merge_column_wise([batch, results])
            if self.node.do_unnest:
                outcomes.unnest(results.columns)
            yield outcomes
