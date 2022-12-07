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
import os
from typing import Callable, List, Tuple

import pandas as pd

from eva.catalog.models.udf_io import UdfIO
from eva.constants import NO_GPU
from eva.executor.execution_context import Context
from eva.expression.abstract_expression import AbstractExpression, ExpressionType
from eva.models.storage.batch import Batch
from eva.parser.alias import Alias
from eva.udfs.gpu_compatible import GPUCompatible

from eva.configuration.configuration_manager import ConfigurationManager

import re

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
        **kwargs
    ):

        super().__init__(ExpressionType.FUNCTION_EXPRESSION, **kwargs)
        self._context = Context()
        self._name = name
        self._function = func
        self._output = output
        self.alias = alias
        self.output_objs: List[UdfIO] = []
        self.projection_columns: List[str] = []

        try:
            gpu=self._context.gpu_device()
            print(f'\n\nWill use {"GPU-{}".format(gpu) if gpu != NO_GPU else "CPU"} for {self.name}\n\n')
        except:
            ...

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

    def get_id_col_name(self, batch: Batch) -> str:
        df = batch.frames
        df_cols = df.columns.tolist()

        # check if this batch data contains table name and frame id
        id_cols = list(filter(lambda x: re.match(r'.*\.id$', x) is not None, df_cols))
        if not (len(id_cols) == 1):
            return None

        return id_cols[0]

    def _check_has_cache(self, batch: Batch) -> Tuple[bool, pd.DataFrame]:
        id_col = self.get_id_col_name(batch)
        if id_col is None:
            return False, None

        table_name_lower_case = id_col.split(".")[0]
        from eva.catalog.catalog_manager import CatalogManager
        cache_meta = CatalogManager().get_res_cache(table_name_lower_case, self.name, ignore_case=True)

        if cache_meta is None:
            return False, None

        index_dir = ConfigurationManager().get_index_dir()
        cache_file_path = os.path.join(index_dir, cache_meta.res_cache_path)

        cached_data = pd.read_pickle(cache_file_path)
        cached_cols = cached_data.columns.tolist()

        for i in range(len(cached_cols)):
            cached_cols[i] = cached_cols[i].split(".")[1]

        cached_data.columns = cached_cols

        for col in self.projection_columns:
            if not (col in cached_cols):
                return False, None

        return True, cached_data

    def evaluate(self, batch: Batch, **kwargs) -> Batch:
        new_batch = batch
        child_batches = [child.evaluate(batch, **kwargs) for child in self.children]
        if len(child_batches):
            new_batch = Batch.merge_column_wise(child_batches)

        has_cache, cached_data = self._check_has_cache(batch)

        outcomes = None
        if has_cache:
            id_col = self.get_id_col_name(batch)
            ids = batch.frames[id_col]

            outcomes = cached_data.iloc[ids].reset_index(drop=True)
            outcomes = Batch(frames=outcomes)

        else:
            func = self._gpu_enabled_function()
            outcomes = func(new_batch.frames)
            outcomes = Batch(pd.DataFrame(outcomes))

        outcomes = outcomes.project(self.projection_columns)
        outcomes.modify_column_alias(self.alias)
        return outcomes

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
