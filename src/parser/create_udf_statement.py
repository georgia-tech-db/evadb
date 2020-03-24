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

from src.parser.statement import AbstractStatement

from src.parser.types import StatementType
from typing import List
from src.parser.types import ParserColumnDataType
from src.parser.create_statement import ColumnDefinition
from pathlib import Path


class CreateUDFStatement(AbstractStatement):
    """Create UDF Statement constructed after parsing the input query

    Attributes:
        name: str
            udf_name provided by the user required
        if_not_exists: bool
            if true should throw an error if udf with same name exists 
            else will replace the existing
        inputs: List[ColumnDefinition]
            udf inputs, represented similar to a table column definition
        outputs: List[ColumnDefinition]
            udf outputs, represented similar to a table column definition
        impl_file_path: str
            file path which holds the implementation of the udf. 
            This file should be placed in the UDF directory and
            the path provided should be relative to the UDF dir.
        type: str
            udf type. it ca be object detection, classification etc.
    """

    def __init__(self,
                 name: str,
                 if_not_exists: bool,
                 inputs: List[ColumnDefinition],
                 outputs: List[ColumnDefinition],
                 impl_file_path: str,
                 type: str = None):
        super().__init__(StatementType.CREATE_UDF)
        self._name = name
        self._if_not_exists = if_not_exists
        self._inputs = inputs
        self._outputs = outputs
        self._impl_file_path = Path(impl_file_path)
        self._type = type

    def __str__(self) -> str:
        print_str = 'CREATE UDF {} INPUT ({}) OUTPUT ({}) TYPE {} IMPL {}'. \
                    format(self._name, self._inputs, self._outputs, self._type,
                           self._impl_path.name)
        return print_str

    @property
    def name(self):
        return self._name

    @property
    def if_not_exists(self):
        return self._if_not_exists

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
    def type(self):
        return self._type
