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

from src.planner.function_scan_plan import FunctionScanPlan
from src.executor.abstract_executor import AbstractExecutor
from src.models.storage.batch import Batch


class FunctionScanExecutor(AbstractExecutor):
    """
    Executes functional expression which yields a table of rows
    Arguments:
        node (AbstractPlan): FunctionScanPlan

    """

    def __init__(self, node: FunctionScanPlan):
        super().__init__(node)
        self.func_expr = node.func_expr

    def validate(self):
        pass

    def exec(self, lateral_input: Batch, *args, **kwargs) -> Iterator[Batch]:
        # this should be the leaf node in the execution plan
        # assert(len(self.self.func_exprchildren) == 0)
        # batch = kwargs.pop(lateral_input, Batch())

        if not lateral_input.empty():
            res = self.func_expr.evaluate(lateral_input)
            batch = Batch.merge_column_wise([res, lateral_input])
            
            if not batch.empty():
                yield batch
