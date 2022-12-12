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
from eva.planner.function_scan_plan import FunctionScanPlan


class FunctionScanExecutor(AbstractExecutor):
    """
    Executes functional expression which yields a table of rows
    Arguments:
        node (AbstractPlan): FunctionScanPlan

    """

    def __init__(self, node: FunctionScanPlan):
        super().__init__(node)
        self.func_expr = node.func_expr
        self.do_unnest = node.do_unnest

    def validate(self):
        pass

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        assert (
            "lateral_input" in kwargs
        ), "Key lateral_input not passed to the FunctionScan"
        lateral_input = kwargs.get("lateral_input")
        if not lateral_input.empty():
            res = self.func_expr.evaluate(lateral_input)
            if not res.empty():
                if self.do_unnest:
                    res.unnest()

                yield res
