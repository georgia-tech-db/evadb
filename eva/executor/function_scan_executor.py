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
from time import time
from typing import Iterator

from eva.catalog.catalog_manager import CatalogManager
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError
from eva.models.storage.batch import Batch
from eva.plan_nodes.function_scan_plan import FunctionScanPlan
from eva.utils.logging_manager import logger


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

    def persistCost(self, name, type, frame_count, resolution, time):
        # TODO: compute cost using time
        cost = time
        catalog_manager = CatalogManager()
        catalog_manager.insert_udf_cost_catalog_entry(
            name, type, cost, frame_count, resolution
        )

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        assert (
            "lateral_input" in kwargs
        ), "Key lateral_input not passed to the FunctionScan"
        lateral_input = kwargs.get("lateral_input")
        catalog_manager = CatalogManager()
        try:
            if not lateral_input.empty():
                t_start = time()
                res = self.func_expr.evaluate(lateral_input)
                t_end = time()
                time_taken = t_end - t_start
                resolution = None
                udf_obj = catalog_manager.get_udf_catalog_entry_by_name(
                    self.func_expr.name
                )
                if udf_obj:
                    type = udf_obj.type
                else:
                    type = None
                self.persistCost(
                    self.func_expr.name,
                    type,
                    lateral_input.frames.shape[0],
                    resolution,
                    time_taken,
                )
                if not res.empty():
                    if self.do_unnest:
                        res.unnest()

                    yield res
        except Exception as e:
            logger.error(e)
            raise ExecutorError(e)
