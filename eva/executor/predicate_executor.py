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

from eva.configuration.configuration_manager import ConfigurationManager
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import apply_predicate, apply_predicate_distributed
from eva.expression.function_expression import FunctionExpression
from eva.models.storage.batch import Batch
from eva.plan_nodes.predicate_plan import PredicatePlan
from itertools import islice

def batched(iterable, n):
    """    
    Batch data into tuples of length n. The last batch may be shorter.
    e.g. batched('ABCDEFG', 3) --> ABC DEF G

    Note: This is copied from the implementation of itertools.batched available from python3.12 onwards
    """
    
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while batch := list(islice(it, n)):
        yield batch

class PredicateExecutor(AbstractExecutor):
    """ """

    def __init__(self, node: PredicatePlan):
        super().__init__(node)
        self.predicate = node.predicate

    def has_function_expr_child (self, expr):
        if (isinstance(expr, FunctionExpression)):
            return True
        return any(self.has_function_expr_child(child) for child in expr.children)

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        child_executor = self.children[0]
        ray_enabled = ConfigurationManager().get_value("experimental", "ray_predicate") and self.has_function_expr_child(self.predicate)
        batches = child_executor.exec(**kwargs)
        if (ray_enabled):
            ray_parallelism = ConfigurationManager().get_value("experimental", "ray_parallelism")
            for batch_list in batched(batches, ray_parallelism):
                output_batches = apply_predicate_distributed(batch_list, self.predicate, ray_parallelism)
                for op_batch in output_batches:
                    if not op_batch.empty():
                        yield op_batch
        else:
            for batch in batches:
                batch = apply_predicate(batch, self.predicate)
                if not batch.empty():
                    yield batch

            
