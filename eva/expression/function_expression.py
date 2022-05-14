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
import pandas as pd
from typing import Callable, List

from eva.catalog.models.udf_io import UdfIO
from eva.constants import NO_GPU
from eva.executor.execution_context import Context
from eva.expression.abstract_expression import AbstractExpression, \
    ExpressionType
from eva.models.storage.batch import Batch
from eva.udfs.gpu_compatible import GPUCompatible


class FunctionExpression(AbstractExpression):
    """
    Consider FunctionExpression: ObjDetector -> (labels, boxes)

    `output`: If the user wants only subset of ouputs. Eg,
    ObjDetector.lables the parser with set output to 'labels'

    `ourput_col_aliases`: It is populated by the binder. In case the
    output is None, the binder sets output_col_aliases to list of all
    output columns of the FunctionExpression. Eg, ['labels',
    'boxes']. Otherwise, only the output columns.

    FunctionExpression also needs to prepend its alias to all the
    projected columns. This is important as other parts of the query
    might be assessing the results using alias. Eg,
    `Select OD.labels FROM Video JOIN LATERAL ObjDetector AS OD;`
    """

    def __init__(self, func: Callable, name: str,
                 output=None, alias=None, **kwargs):

        super().__init__(ExpressionType.FUNCTION_EXPRESSION, **kwargs)
        self._context = Context()
        self._name = name
        self._function = func
        self._output: str = output
        self.alias: str = alias
        self.output_col_aliases: List[str] = []
        self.output_objs: List[UdfIO] = []

    @property
    def name(self):
        return self._name

    @property
    def output(self):
        return self._output

    @property
    def function(self):
        return self._function

    @function.setter
    def function(self, func: Callable):
        self._function = func

    def evaluate(self, batch: Batch, **kwargs):
        new_batch = batch
        child_batches = \
            [child.evaluate(batch, **kwargs) for child in self.children]
        if len(child_batches):
            new_batch = Batch.merge_column_wise(child_batches)

        func = self._gpu_enabled_function()
        outcomes = func(new_batch.frames)
        outcomes = Batch(pd.DataFrame(outcomes))

        outcomes.modify_column_alias(self.alias)

        return outcomes.project(self.output_col_aliases)

    def _gpu_enabled_function(self):
        if isinstance(self._function, GPUCompatible):
            device = self._context.gpu_device()
            if device != NO_GPU:
                return self._function.to_device(device)
        return self._function

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, FunctionExpression):
            return False
        return (is_subtree_equal and self.name == other.name
                and self.output == other.output
                and self.alias == other.alias
                and self.output_col_aliases == other.output_col_aliases
                and self.function == other.function
                and self.output_objs == other.output_objs)

    def __hash__(self) -> int:
        return hash((super().__hash__(),
                     self.name,
                     self.output,
                     self.alias,
                     tuple(self.output_col_aliases),
                     self.function,
                     tuple(self.output_objs)))
