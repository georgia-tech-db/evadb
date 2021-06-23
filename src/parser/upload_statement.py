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
from pathlib import Path


class UploadStatement(AbstractStatement):
    """
    Load Data Statement constructed after parsing the input query

    Arguments:
    table (TableRef): table reference to load into
    path (str): path from where data needs to be loaded
    """

    def __init__(self, infile: str, path: str):
        super().__init__(StatementType.UPLOAD)
        self._infile = Path(infile)
        self._path = Path(path)

    def __str__(self) -> str:
        print_str = "UPLOAD INFILE {} PATH {}".format(
            self._infile.name, self._path.name)
        return print_str

    @property
    def path(self) -> Path:
        return self._path

    def __eq__(self, other):
        if not isinstance(other, UploadStatement):
            return False
        return (self._infile == other.infile and
                self.path == other.path)
