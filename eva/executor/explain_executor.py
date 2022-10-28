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
import pandas as pd

from eva.executor.abstract_executor import AbstractExecutor
from eva.models.storage.batch import Batch
from eva.planner.explain_plan import ExplainPlan
from eva.planner.abstract_plan import AbstractPlan


class ExplainExecutor(AbstractExecutor):
    def __init__(self, node: ExplainPlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self):
        yield Batch(pd.DataFrame([self._exec(self._node.explainable_plan)]))

    def _exec(self, node: AbstractPlan, depth: int):
        cur_str = " " * depth * 4 + "|__ " + str(node) + "\n"
        for child in node.children:
            cur_str += self.exec(child, depth + 1)
        return cur_str