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
from eva.planner.pp_plan import PPScanPlan


class PPExecutor(AbstractExecutor):
    """
    Applies PP to filter out the frames that doesn't satisfy the condition
    Arguments:
        node (AbstractPlan): ...

    Note: This look kind of redundant. This logic for now is similar to that
    of sequential scan executor. Will decide to delete it depending on how
    sequential scan evolves.
    """

    def __init__(self, node: PPScanPlan):
        super().__init__(node)
        self.predicate = node.predicate

    def validate(self):
        pass

    def exec(self) -> Iterator[Batch]:
        child_executor = self.children[0]
        for batch in child_executor.exec():
            outcomes = self.predicate.evaluate(batch)
            required_frame_ids = []
            for i, outcome in enumerate(outcomes):
                if outcome:
                    required_frame_ids.append(i)

            yield batch[required_frame_ids]
