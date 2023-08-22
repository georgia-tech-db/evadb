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
from pathlib import Path
from typing import List, Tuple

from evadb.parser.create_statement import ColumnDefinition
from evadb.parser.select_statement import SelectStatement
from evadb.parser.statement import AbstractStatement
from evadb.parser.types import StatementType


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
        query: SelectStatement
            data source for the model train or fine tune.
        udf_type: str
            udf type. it can be object detection, classification etc.
        metadata: List[Tuple[str, str]]
            metadata, list of key value pairs used for storing metadata of udfs, mostly used for advanced udf types
    """

    def __init__(
        self,
        name: str,
        if_not_exists: bool,
        impl_path: str,
        inputs: List[ColumnDefinition] = [],
        outputs: List[ColumnDefinition] = [],
        udf_type: str = None,
        query: SelectStatement = None,
        metadata: List[Tuple[str, str]] = None,
    ):
        super().__init__(StatementType.CREATE_UDF)
        self._name = name
        self._if_not_exists = if_not_exists
        self._inputs = inputs
        self._outputs = outputs
        self._impl_path = Path(impl_path) if impl_path else None
        self._udf_type = udf_type
        self._query = query
        self._metadata = metadata

    def __str__(self) -> str:
        s = "CREATE UDF"

        if self._if_not_exists:
            s += " IF NOT EXISTS"

        s += " " + self._name

        if self._query is not None:
            s += f" FROM ({self._query})"

        if self._udf_type is not None:
            s += " TYPE " + str(self._udf_type)

        if self._impl_path:
            s += f" IMPL {self._impl_path.name}"

        if self._metadata is not None:
            for key, value in self._metadata:
                s += f" '{key}' '{value}'"
        return s

    @property
    def name(self):
        return self._name

    @property
    def if_not_exists(self):
        return self._if_not_exists

    @property
    def inputs(self):
        return self._inputs

    @inputs.setter
    def inputs(self, value):
        self._inputs = value

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, value):
        self._outputs = value

    @property
    def impl_path(self):
        return self._impl_path

    @property
    def udf_type(self):
        return self._udf_type

    @property
    def query(self):
        return self._query

    @property
    def metadata(self):
        return self._metadata

    def __eq__(self, other):
        if not isinstance(other, CreateUDFStatement):
            return False
        return (
            self.name == other.name
            and self.if_not_exists == other.if_not_exists
            and self.inputs == other.inputs
            and self.outputs == other.outputs
            and self.impl_path == other.impl_path
            and self.udf_type == other.udf_type
            and self.query == other.query
            and self.metadata == other.metadata
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.name,
                self.if_not_exists,
                tuple(self.inputs),
                tuple(self.outputs),
                self.impl_path,
                self.udf_type,
                self.query,
                tuple(self.metadata),
            )
        )
