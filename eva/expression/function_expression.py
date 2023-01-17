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
from typing import Callable, List

from eva.catalog.models.udf_catalog import UdfCatalogEntry
from eva.catalog.models.udf_io_catalog import UdfIOCatalogEntry
from eva.constants import NO_GPU
from eva.executor.execution_context import Context
from eva.expression.abstract_expression import AbstractExpression, ExpressionType
from eva.models.storage.batch import Batch
from eva.parser.alias import Alias
from eva.udfs.gpu_compatible import GPUCompatible


class FunctionExpression(AbstractExpression):
    """
    Consider FunctionExpression: ObjDetector -> (labels, boxes)

    `output`: If the user wants only subset of ouputs. Eg,
    ObjDetector.lables the parser with set output to 'labels'

    `output_objs`: It is populated by the binder. In case the
    output is None, the binder sets output_objs to list of all
    output columns of the FunctionExpression. Eg, ['labels',
    'boxes']. Otherwise, only the output columns.

    FunctionExpression also needs to prepend its alias to all the
    projected columns. This is important as other parts of the query
    might be assessing the results using alias. Eg,
    `Select OD.labels FROM Video JOIN LATERAL ObjDetector AS OD;`
    """

    def __init__(
        self,
        func: Callable,
        name: str,
        output: str = None,
        alias: Alias = None,
        **kwargs,
    ):

        super().__init__(ExpressionType.FUNCTION_EXPRESSION, **kwargs)
        self._context = Context()
        self._name = name
        self._function = func
        self._function_instance = None
        self._output = output
        self.alias = alias
        self.udf_obj: UdfCatalogEntry = None
        self.output_objs: List[UdfIOCatalogEntry] = []
        self.projection_columns: List[str] = []

    @property
    def name(self):
        return self._name

    @property
    def output(self):
        return self._output

    @property
    def col_alias(self):
        col_alias_list = []
        if self.alias is not None:
            for col in self.alias.col_names:
                col_alias_list.append("{}.{}".format(self.alias.alias_name, col))
        return col_alias_list

    @property
    def function(self):
        return self._function

    @function.setter
    def function(self, func: Callable):
        self._function = func

    def evaluate(self, batch: Batch, **kwargs) -> Batch:
        new_batch = batch
        child_batches = [child.evaluate(batch, **kwargs) for child in self.children]

        if len(child_batches):
            batch_sizes = [len(child_batch) for child_batch in child_batches]
            are_all_equal_length = all(batch_sizes[0] == x for x in batch_sizes)
            maximum_batch_size = max(batch_sizes)
            if not are_all_equal_length:
                for child_batch in child_batches:
                    if len(child_batch) != maximum_batch_size:
                        if len(child_batch) == 1:
                            # duplicate row inplace
                            child_batch.repeat(maximum_batch_size)
                        else:
                            raise Exception(
                                "Not all columns in the batch have equal elements"
                            )
            new_batch = Batch.merge_column_wise(child_batches)

        func = self._gpu_enabled_function()
        outcomes = new_batch
        outcomes.apply_function_expression(func)
        outcomes = outcomes.project(self.projection_columns)
        outcomes.modify_column_alias(self.alias)
        return outcomes

    def signature(self) -> str:
        """It constructs the signature of the function expression.
        It traverses the children (function arguments) and compute signature for each child. The output is in the form `udf_name(arg1, arg2, ...)`.

        Returns:
            str: signature string
        """
        child_sigs = []
        for child in self.children:
            child_sigs.append(child.signature())

        func_sig = f"{self.name}({','.join(child_sigs)})"
        if self._output and len(self.udf_obj.outputs) > 1:
            # In this situation, the function expression has multiple output columns,
            # but only one of them is projected. As a result, we must generate a
            # signature that includes only the projected column in order to distinguish
            # it from the scenario where all columns are projected.
            func_sig = f"{func_sig}.{self.output_objs[0].name}"

        return func_sig

    def _gpu_enabled_function(self):
        if self._function_instance is None:
            self._function_instance = self.function()
            if isinstance(self._function_instance, GPUCompatible):
                device = self._context.gpu_device()
                if device != NO_GPU:
                    self._function_instance = self._function_instance.to_device(device)
        return self._function_instance

    def __str__(self) -> str:
        expr_str = f"{self.name}()"
        return expr_str

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, FunctionExpression):
            return False
        return (
            is_subtree_equal
            and self.name == other.name
            and self.output == other.output
            and self.alias == other.alias
            and self.function == other.function
            and self.output_objs == other.output_objs
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.name,
                self.output,
                self.alias,
                self.function,
                tuple(self.output_objs),
            )
        )
