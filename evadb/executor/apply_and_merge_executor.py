# coding=utf-8
# Copyright 2018-2023 EvaDB
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

from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.models.storage.batch import Batch
from evadb.plan_nodes.apply_and_merge_plan import ApplyAndMergePlan


class ApplyAndMergeExecutor(AbstractExecutor):
    """
    Apply the function expression to the input data, merge the output of the function
    with the input data, and yield the result to the parent. The current implementation
    assumes an inner join while merging. Therefore, if the function does not return any
    output, the input rows are dropped.
    Arguments:
        node (AbstractPlan): ApplyAndMergePlan

    """

    def __init__(self, db: EvaDBDatabase, node: ApplyAndMergePlan):
        super().__init__(db, node)
        self.func_expr = node.func_expr
        self.do_unnest = node.do_unnest
        self.alias = node.alias

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        child_executor = self.children[0]
        for batch in child_executor.exec(**kwargs):
            func_result = self.func_expr.evaluate(batch)

            # persist stats of function expression
            if self.func_expr.udf_obj and self.func_expr._stats:
                udf_id = self.func_expr.udf_obj.row_id
                self.catalog().upsert_udf_cost_catalog_entry(
                    udf_id, self.func_expr.udf_obj.name, self.func_expr._stats.prev_cost
                )

            output = Batch.merge_column_wise([batch, func_result])
            if self.do_unnest:
                output.unnest(func_result.columns)
                # we reset the index as after unnest there can be duplicate index
                output.reset_index()

            yield output
