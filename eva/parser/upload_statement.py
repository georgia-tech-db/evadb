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
from pathlib import Path
from typing import List

from eva.expression.abstract_expression import AbstractExpression
from eva.parser.statement import AbstractStatement
from eva.parser.table_ref import TableInfo
from eva.parser.types import StatementType


class UploadStatement(AbstractStatement):
    """
    Upload Statement constructed after parsing the input query

    Arguments:
        path(Path): file path (with prefix prepended) where
                    the data is uploaded
        video_blob(str): base64 encoded video string
    """

    def __init__(
        self,
        path: str,
        video_blob: str,
        table_info: str,
        column_list: List[AbstractExpression] = None,
        file_options: dict = None,
    ):
        super().__init__(StatementType.UPLOAD)
        self._path = Path(path)
        self._video_blob = video_blob
        self._table_info = table_info
        self._column_list = column_list
        self._file_options = file_options

    def __str__(self) -> str:
        column_list_str = ""
        if self._column_list is not None:
            for col in self._column_list:
                column_list_str += str(col) + ", "
            column_list_str = column_list_str.rstrip(", ")

        file_option_str = ""
        for key, value in self._file_options.items():
            file_option_str += f"{str(key)}: {str(value)}"

        upload_stmt_str = ""
        if self._column_list is None:
            upload_stmt_str = "UPLOAD PATH {} BLOB {} INTO {} WITH {}".format(
                self._path.name, "video blob", self._table_info, file_option_str
            )
        else:
            upload_stmt_str = "UPLOAD PATH {} BLOB {} INTO {} ({}) WITH {}".format(
                self._path.name,
                "video blob",
                self._table_info,
                column_list_str,
                file_option_str,
            )
        return upload_stmt_str

    @property
    def path(self) -> Path:
        return self._path

    @property
    def video_blob(self) -> str:
        return self._video_blob

    @property
    def table_info(self) -> TableInfo:
        return self._table_info

    @property
    def column_list(self) -> List[AbstractExpression]:
        return self._column_list

    @column_list.setter
    def column_list(self, col_list: List[AbstractExpression]):
        self._column_list = col_list

    @property
    def file_options(self) -> dict:
        return self._file_options

    def __eq__(self, other):
        if not isinstance(other, UploadStatement):
            return False
        return (
            self.path == other.path
            and self.video_blob == other.video_blob
            and self.table_info == other.table_info
            and self.column_list == other.column_list
            and self.file_options == other.file_options
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.path,
                self.video_blob,
                self.table_info,
                tuple(self.column_list or []),
                frozenset(self.file_options.items()),
            )
        )
