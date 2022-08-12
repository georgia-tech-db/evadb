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

from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.expression.abstract_expression import AbstractExpression
from eva.planner.abstract_plan import AbstractPlan
from eva.planner.types import PlanOprType


class UploadPlan(AbstractPlan):
    """
    This plan is used for storing information required for upload
    operations.

    Arguments:
        path(Path): file path (with prefix prepended) where
                    the data is uploaded
        video_blob(str): base64 encoded video string
    """

    def __init__(
        self,
        file_path: Path,
        video_blob: str,
        table_metainfo: DataFrameMetadata,
        batch_mem_size: int,
        column_list: List[AbstractExpression] = None,
        file_options: dict = None,
    ):
        super().__init__(PlanOprType.UPLOAD)
        self._file_path = file_path
        self._video_blob = video_blob
        self._table_metainfo = table_metainfo
        self._batch_mem_size = batch_mem_size
        self._column_list = column_list
        self._file_options = file_options

    @property
    def file_path(self):
        return self._file_path

    @property
    def video_blob(self):
        return self._video_blob

    @property
    def table_metainfo(self):
        return self._table_metainfo

    @property
    def batch_mem_size(self):
        return self._batch_mem_size

    @property
    def column_list(self):
        return self._column_list

    @property
    def file_options(self):
        return self._file_options

    def __str__(self):
        return "UploadPlan(file_path={}, \
            video_blob={}, \
            table_id={}, \
            batch_mem_size={}, \
            column_list={}, \
            file_options={})".format(
            self.file_path,
            "string of video blob",
            self.table_metainfo,
            self.batch_mem_size,
            self.column_list,
            self.file_options,
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.file_path,
                self.video_blob,
                self.table_metainfo,
                self.batch_mem_size,
                tuple(self.column_list),
                frozenset(self.file_options.items()),
            )
        )
