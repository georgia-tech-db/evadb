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
# See the License for the specific language governing perkmissions and
# limitations under the License.
from typing import List

from eva.parser.statement import AbstractStatement
from eva.parser.types import StatementType
from eva.parser.create_statement import ColumnDefinition
from pathlib import Path

class DropUDFStatement(AbstractStatement):
    """Drop Udf Statement constructed after parsing the input query

    Attributes:
        name: name of the udf
        inputs: inputs to the udf
        outputs: outputs to the udf
        impl_file_path: file path which holds the implementation of the udf
        udf_type: type of the udf (eg. object detection, classification etc.)
    """

    def __init__(self,
                 name: str,
                 if_exists: bool,
                 inputs: List[ColumnDefinition],
                 outputs: List[ColumnDefinition],
                 impl_path: str,
                 udf_type: str = None):
        super().__init__(StatementType.DROP_UDF)
        self._name = name
        self._if_exists = if_exists
        self._inputs = inputs
        self._outputs = outputs
        self._impl_path = Path(impl_path)
        self._udf_type = udf_type

    def __str__(self) -> str:
        if self._if_exists:
            print_str = 'DROP UDF IF EXISTS {} INPUT ({}) OUTPUT ({}) TYPE {} IMPL {}'. \
                format(self._name, self._inputs, self._outputs,
                        self._udf_type, self._impl_path.name)
        else:
            print_str = 'DROP UDF {} INPUT ({}) OUTPUT ({}) TYPE {} IMPL {}'. \
                format(self._name, self._inputs, self._outputs,
                        self._udf_type, self._impl_path.name)
        return print_str

    @property
    def name(self):
        return self._name

    @property
    def if_exists(self):
        return self._if_exists

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    @property
    def impl_path(self):
        return self._impl_path

    @property
    def udf_type(self):
        return self._udf_type


    def __eq__(self, other):
        if not isinstance(other, DropUDFStatement):
            return False
        return (self.name == other.name
                and self.if_exists == other.if_exists
                and self.inputs == other.inputs
                and self.outputs == other.outputs
                and self.impl_path == other.impl_path
                and self.udf_type == other.udf_type)

    def __hash__(self) -> int:
        return hash((super().__hash__(),
                     self.name,
                     self.if_exists,
                     tuple(self.inputs),
                     tuple(self.outputs,
                     self.impl_path,
                     self.udf_type)))