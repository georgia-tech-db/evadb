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

import numpy as np
import pandas as pd

from eva.executor.abstract_executor import AbstractExecutor
from eva.models.storage.batch import Batch
from eva.plan_nodes.extract_object_plan import ExtractObjectPlan


class ExtractObjectExecutor(AbstractExecutor):
    """ """

    def __init__(self, node: ExtractObjectPlan):
        super().__init__(node)
        self.detector = node.detector
        self.tracker = node.tracker.function()
        self.tracker_args = node.tracker_args

    def validate(self):
        pass

    def exec(self) -> Iterator[Batch]:
        child_executor = self.children[0]
        for batch in child_executor.exec():
            objects = self.detector.evaluate(batch)

            # send row by row to the tracker
            results = []
            for (_, row1), (_, row2) in zip(batch.iterrows(), objects.iterrows()):
                results.append(
                    self.tracker(
                        np.array(row1[0]),
                        np.array(row1[1]),
                        np.stack(row2[0]),
                        np.stack(row2[1]),
                        np.stack(row2[2]),
                    )
                )

            outcomes = Batch(pd.DataFrame(results, columns=self.node.expr.col_alias))
            outcomes = Batch.merge_column_wise([batch, outcomes])
            if self.node.do_unnest:
                outcomes.unnest(self.node.expr.col_alias)
            yield outcomes
