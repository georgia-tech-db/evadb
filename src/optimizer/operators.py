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
from enum import IntEnum, unique
from typing import List

from src.catalog.models.df_metadata import DataFrameMetadata
from src.parser.table_ref import TableRef
from src.expression.abstract_expression import AbstractExpression
from src.catalog.models.df_column import DataFrameColumn


@unique
class OperatorType(IntEnum):
    """
    Manages enums for all the operators supported
    """
    LOGICALGET = 1,
    LOGICALFILTER = 2,
    LOGICALPROJECT = 3,
    LOGICALINSERT = 4,
    LOGICALCREATE = 5,


class Operator:
    """Base class for logital plan of operators

    Arguments:
        op_type: {OperatorType} -- {the opr type held by this node}
        children: {List} -- {the list of operator children for this node}
    """

    def __init__(self, op_type: OperatorType, children: List = None):
        self._type = op_type
        self._children = children if children is not None else []

    def append_child(self, child: 'Operator'):
        if self._children is None:
            self._children = []

        self._children.append(child)

    @property
    def children(self):
        return self._children

    @property
    def type(self):
        return self._type


class LogicalGet(Operator):
    def __init__(self, video: TableRef, dataset_metadata: DataFrameMetadata,
                 children: List = None):
        super().__init__(OperatorType.LOGICALGET, children)
        self._video = video
        self._dataset_metadata = dataset_metadata

    @property
    def video(self):
        return self._video

    @property
    def dataset_metadata(self):
        return self._dataset_metadata


class LogicalFilter(Operator):
    def __init__(self, predicate: AbstractExpression, children: List = None):
        super().__init__(OperatorType.LOGICALFILTER, children)
        self._predicate = predicate

    @property
    def predicate(self):
        return self._predicate


class LogicalProject(Operator):
    def __init__(self, target_list: List[AbstractExpression],
                 children: List = None):
        super().__init__(OperatorType.LOGICALPROJECT, children)
        self._target_list = target_list

    @property
    def target_list(self):
        return self._target_list


class LogicalInsert(Operator):
    """[Logical Node for Insert operation]

    Arguments:
        video {TableRef}:
            [TableRef object copied from parsed statement]
        video_catalog_id{int}:
            [catalog id for the video table]
        column_list{List[AbstractExpression]}:
            [After binding annotated column_list]
        value_list{List[AbstractExpression]}:
            [value list to insert]
    """

    def __init__(self, video: TableRef, video_catalog_id: int,
                 column_list: List[AbstractExpression],
                 value_list: List[AbstractExpression],
                 children: List = None):
        super().__init__(OperatorType.LOGICALINSERT, children)
        self._video = video
        self._video_catalog_id = video_catalog_id
        self._column_list = column_list
        self._value_list = value_list

    @property
    def video(self):
        return self._video

    @property
    def video_catalog_id(self):
        return self._video_catalog_id

    @property
    def value_list(self):
        return self._value_list

    @property
    def column_list(self):
        return self._column_list


class LogicalCreate(Operator):
    """Logical node for insert operations

    Arguments:
        video {TableRef}: [video table that is to be created]
        column_list {List[AbstractExpression]}:
            [After binding annotated column_list]
        if_not_exists {bool}: [create table if exists]

    """

    def __init__(self, video: TableRef, column_list: List[DataFrameColumn],
                 if_not_exists: bool = False, children=None):
        super().__init__(OperatorType.LOGICALCREATE, children)
        self._video = video
        self._column_list = column_list
        self._if_not_exists = if_not_exists

    @property
    def video(self):
        return self._video

    @property
    def column_list(self):
        return self._column_list

    @property
    def if_not_exists(self):
        return self._if_not_exists
