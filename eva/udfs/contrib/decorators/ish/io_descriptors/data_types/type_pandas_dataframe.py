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
import pandas as pd

from eva.udfs.contrib.decorators.ish.io_descriptors.eva_arguments import EvaArgument


class PandasDataframe(EvaArgument):
    def __init__(self, columns) -> None:
        super().__init__()
        self.columns = columns

    def check_column_names(self, input_object):
        obj_cols = list(input_object.columns)
        return obj_cols == self.columns

    def check_type(self, input_object) -> bool:
        return isinstance(input_object, pd.DataFrame)

    def is_output_columns_set(self):
        return not (self.columns is None)

    def name(self):
        return "PandasDataframe"
