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

from eva.parser.statement import AbstractStatement

from eva.parser.types import StatementType
from pathlib import Path


class UploadStatement(AbstractStatement):
    """
    Upload Statement constructed after parsing the input query

    Arguments:
        path(Path): file path (with prefix prepended) where
                    the data is uploaded
        video_blob(str): base64 encoded video string
    """

    def __init__(self, path: str, video_blob: str):
        super().__init__(StatementType.UPLOAD)
        self._path = Path(path)
        self._video_blob = video_blob

    def __str__(self) -> str:
        print_str = "UPLOAD PATH {} BLOB {}".format(
            self._path, "string of video blob")
        return print_str

    @property
    def path(self) -> Path:
        return self._path

    @property
    def video_blob(self) -> str:
        return self._video_blob

    def __eq__(self, other):
        if not isinstance(other, UploadStatement):
            return False
        return (self.path == other.path and
                self.video_blob == other.video_blob)
