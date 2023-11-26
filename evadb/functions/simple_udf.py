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
import numpy as np
import pandas as pd
import importlib
import pickle
from pathlib import Path
import typing

from evadb.catalog.catalog_type import NdArrayType
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward, setup
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe
from evadb.configuration.constants import EvaDB_ROOT_DIR

class SimpleUDF(AbstractFunction):
    @setup(cacheable=False, function_type="SimpleUDF", batchable=False)
    def setup(self):
        in_labels = []
        in_types = []
        for label in self.types:
            if label == "return": continue
            in_labels.append(label)
            in_types.append(self.convert_python_types(self.types[label]))
        out_types = [self.convert_python_types(self.types['return'])]

        self.forward.tags["input"] = [PandasDataframe(
            columns=in_labels,
            column_types=in_types,
            column_shapes=[(1) * len(in_labels)]
        )]

        self.forward.tags["output"] = [PandasDataframe(
            columns=["output"],
            column_types=out_types,
            column_shapes=[(1) * len(out_types)],
        )]

    @property
    def name(self) -> str:
        return "SimpleUDF"

    @forward(None, None)
    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        def _forward(row: pd.Series) -> np.ndarray:
            temp = self.udf
            return temp(row)
            
        ret = pd.DataFrame()
        ret["output"] = df.apply(_forward, axis=1)
        return ret
    
    def set_udf(self, classname:str, filepath: str):
        if f"{EvaDB_ROOT_DIR}/simple_udfs/" in filepath:
            f = open(f"{EvaDB_ROOT_DIR}/simple_udfs/Func_SimpleUDF", 'rb')
            self.udf = pickle.load(f)
        else:
            try:
                abs_path = Path(filepath).resolve()
                spec = importlib.util.spec_from_file_location(abs_path.stem, abs_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            except ImportError as e:
                # ImportError in the case when we are able to find the file but not able to load the module
                err_msg = f"ImportError : Couldn't load function from {filepath} : {str(e)}. Not able to load the code provided in the file {abs_path}. Please ensure that the file contains the implementation code for the function."
                raise ImportError(err_msg)
            except FileNotFoundError as e:
                # FileNotFoundError in the case when we are not able to find the file at all at the path.
                err_msg = f"FileNotFoundError : Couldn't load function from {filepath} : {str(e)}. This might be because the function implementation file does not exist. Please ensure the file exists at {abs_path}"
                raise FileNotFoundError(err_msg)
            except Exception as e:
                # Default exception, we don't know what exactly went wrong so we just output the error message
                err_msg = f"Couldn't load function from {filepath} : {str(e)}."
                raise RuntimeError(err_msg)
            
            # Try to load the specified class by name
            if classname and hasattr(module, classname):
                self.udf = getattr(module, classname)

        self.types = typing.get_type_hints(self.udf)

    def convert_python_types(self, type):
        if type == bool:
            return NdArrayType.BOOL
        elif type == int:
            return NdArrayType.INT32
        elif type == float:
            return NdArrayType.FLOAT32
        elif type == str:
            return NdArrayType.STR
        else:
            return NdArrayType.ANYTYPE