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
import pandas as pd

from evadb.catalog.catalog_type import NdArrayType
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward, setup
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe


class UserDefinedFunction(AbstractFunction):
    """
    Arguments:

    Input Signatures:
        id (int)

    Output Signatures:
        output (int)
    """

    @property
    def name(self) -> str:
        return self._func.__name__

    @setup(cacheable=True, batchable=True)
    def setup(self) -> None:
        import inspect

        sig = inspect.signature(self._func)
        params = sig.parameters
        # assert that all params have a type annotation
        for param in params.values():
            assert (
                param.annotation != inspect.Parameter.empty
            ), f"Parameter {param.name} has no type annotation"
        self._inputs = list(params.values())
        # get the return type annotation
        self._output = sig.return_annotation
        # assert that the return type annotation is not empty
        assert (
            self._output != inspect.Parameter.empty
        ), "Return type annotation is empty"

        input_io_arg = PandasDataframe(
            columns=[x.name for x in self._inputs],
            column_types=[
                NdArrayType.from_python_type(x.annotation) for x in self._inputs
            ],
            column_shapes=[(1,) for x in self._inputs],
        )

        output_io_arg = PandasDataframe(
            columns=[self.name.lower()],
            column_types=[NdArrayType.from_python_type(self._output)],
            column_shapes=[(1,)],
        )

        # set the input and output tags (similar to @forward decorator)
        self.forward.tags["input"] = [input_io_arg]
        self.forward.tags["output"] = [output_io_arg]

    @forward(
        input_signatures=[],
        output_signatures=[],
    )
    def forward(self, in_df: pd.DataFrame):
        out_df = pd.DataFrame()
        # apply the function to each row
        out_df[self.name.lower()] = in_df.apply(self._func, axis=1)

        return out_df


def generate_udf(func):
    class_body = {
        "_func": staticmethod(func),
    }
    return type(func.__name__, (UserDefinedFunction,), class_body)
