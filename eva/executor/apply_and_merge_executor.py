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
from eva.executor.executor_utils import ExecutorError
from eva.models.storage.batch import Batch
from eva.plan_nodes.apply_and_merge_plan import ApplyAndMergePlan
from eva.utils.logging_manager import logger


class ApplyAndMergeExecutor(AbstractExecutor):
    """
    Apply the function expression to the input data, merge the output of the function
    with the input data, and yield the result to the parent. The current implementation
    assumes an inner join while merging. Therefore, if the function does not return any
    output, the input rows are dropped.
    Arguments:
        node (AbstractPlan): ApplyAndMergePlan

    """

    def __init__(self, node: ApplyAndMergePlan):
        super().__init__(node)
        self.func_expr = node.func_expr
        self.do_unnest = node.do_unnest
        self.alias = node.alias

    def validate(self):
        pass

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        child_executor = self.children[0]
        for batch in child_executor.exec(**kwargs):
            res = self.func_expr.evaluate(batch)
            try:
                if not res.empty():
                    if self.do_unnest:
                        res.unnest()

                    # Merge the results to the input.
                    # This assumes that the batch index is preserved by the function
                    # call. Since both the batch and the results are sorted, we could
                    # perform a sorted merge, though the typical small size of the
                    # batch and results should not significantly impact performance.
                    merged_batch = Batch.join(batch, res)
                    merged_batch.reset_index()
                    yield merged_batch
            except Exception as e:
                logger.error(e)
                raise ExecutorError(e)
