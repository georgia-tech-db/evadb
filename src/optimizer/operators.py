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
from enum import IntEnum, unique, auto
from typing import List

from src.catalog.models.df_metadata import DataFrameMetadata
from src.expression.constant_value_expression import ConstantValueExpression
from src.parser.table_ref import TableRef
from src.expression.abstract_expression import AbstractExpression
from src.catalog.models.df_column import DataFrameColumn
from src.catalog.models.udf_io import UdfIO
from pathlib import Path


@unique
class OperatorType(IntEnum):
    """
    Manages enums for all the operators supported
    """
    LOGICALGET = auto()
    LOGICALFILTER = auto()
    LOGICALPROJECT = auto()
    LOGICALINSERT = auto()
    LOGICALCREATE = auto()
    LOGICALCREATEUDF = auto()
    LOGICALLOADDATA = auto()
    LOGICALQUERYDERIVEDGET = auto()
    LOGICALUNION = auto()
    LOGICALORDERBY = auto()
    LOGICALLIMIT = auto()
    LOGICALEXPLODE = auto()


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
        if child:
            self._children.append(child)

    @property
    def children(self):
        return self._children

    @property
    def type(self):
        return self._type

    def __eq__(self, other):
        is_subtree_equal = True
        if not isinstance(other, Operator):
            return False
        if len(self.children) != len(other.children):
            return False
        for child1, child2 in zip(self.children, other.children):
            is_subtree_equal = is_subtree_equal and (child1 == child2)
        return is_subtree_equal


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

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalGet):
            return False
        return (is_subtree_equal
                and self.video == other.video
                and self.dataset_metadata == other.dataset_metadata)


class LogicalQueryDerivedGet(Operator):
    def __init__(self, children: List = None):
        super().__init__(OperatorType.LOGICALQUERYDERIVEDGET,
                         children=children)
        # `TODO` We need to store the alias information here
        # We need construct the map using the target list of the
        # subquery to validate the overall query

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalQueryDerivedGet):
            return False
        return is_subtree_equal


class LogicalFilter(Operator):
    def __init__(self, predicate: AbstractExpression, children: List = None):
        super().__init__(OperatorType.LOGICALFILTER, children)
        self._predicate = predicate

    @property
    def predicate(self):
        return self._predicate

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalFilter):
            return False
        return (is_subtree_equal
                and self.predicate == other.predicate)


class LogicalProject(Operator):
    def __init__(self, target_list: List[AbstractExpression],
                 children: List = None):
        super().__init__(OperatorType.LOGICALPROJECT, children)
        self._target_list = target_list

    @property
    def target_list(self):
        return self._target_list

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalProject):
            return False
        return (is_subtree_equal
                and self.target_list == other.target_list)


class LogicalOrderBy(Operator):
    def __init__(self, orderby_list: List,
                 children: List = None):
        super().__init__(OperatorType.LOGICALORDERBY, children)
        self._orderby_list = orderby_list

    @property
    def orderby_list(self):
        return self._orderby_list

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalOrderBy):
            return False
        return (is_subtree_equal
                and self.orderby_list == other.orderby_list)


class LogicalLimit(Operator):
    def __init__(self, limit_count: ConstantValueExpression,
                 children: List = None):
        super().__init__(OperatorType.LOGICALLIMIT, children)
        self._limit_count = limit_count

    @property
    def limit_count(self):
        return self._limit_count

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalLimit):
            return False
        return (is_subtree_equal
                and self.limit_count == other.limit_count)


class LogicalUnion(Operator):
    def __init__(self, all: bool, children: List = None):
        super().__init__(OperatorType.LOGICALUNION, children)
        self._all = all

    @property
    def all(self):
        return self._all

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalUnion):
            return False
        return (is_subtree_equal and self.all == other.all)


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

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalInsert):
            return False
        return (is_subtree_equal
                and self.video == other.video
                and self.video_catalog_id == other.video_catalog_id
                and self.value_list == other.value_list
                and self.column_list == other.column_list)


class LogicalCreate(Operator):
    """Logical node for create table operations

    Arguments:
        video {TableRef}: [video table that is to be created]
        column_list {List[DataFrameColumn]}:
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

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalCreate):
            return False
        return (is_subtree_equal
                and self.video == other.video
                and self.column_list == other.column_list
                and self.if_not_exists == other.if_not_exists)


class LogicalExplode(Operator):
    """Logical node for explode operation

        Arguments:
            column_list {List[AbstractExpression]}:
    """
    def __init__(self, column_list: List[AbstractExpression],
                 children=None):
        super().__init__(OperatorType.LOGICALEXPLODE, children)
        self._column_list = column_list

    @property
    def column_list(self):
        return self._column_list

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalExplode):
            return False
        return (is_subtree_equal
                and self._column_list == other.column_list)


class LogicalCreateUDF(Operator):
    """
    Logical node for create udf operations

    Attributes:
        name: str
            udf_name provided by the user required
        if_not_exists: bool
            if true should throw an error if udf with same name exists
            else will replace the existing
        inputs: List[UdfIO]
            udf inputs, annotated list similar to table columns
        outputs: List[UdfIO]
            udf outputs, annotated list similar to table columns
        impl_path: Path
            file path which holds the implementation of the udf.
            This file should be placed in the UDF directory and
            the path provided should be relative to the UDF dir.
        udf_type: str
            udf type. it ca be object detection, classification etc.
    """

    def __init__(self, name: str,
                 if_not_exists: bool,
                 inputs: List[UdfIO],
                 outputs: List[UdfIO],
                 impl_path: Path,
                 udf_type: str = None,
                 children=None):
        super().__init__(OperatorType.LOGICALCREATEUDF, children)
        self._name = name
        self._if_not_exists = if_not_exists
        self._inputs = inputs
        self._outputs = outputs
        self._impl_path = impl_path
        self._udf_type = udf_type

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
    def udf_type(self):
        return self._udf_type

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalCreateUDF):
            return False
        return (is_subtree_equal
                and self.name == other.name
                and self.if_not_exists == other.if_not_exists
                and self.inputs == other.inputs
                and self.outputs == other.outputs
                and self.udf_type == other.udf_type
                and self.impl_path == other.impl_path)


class LogicalLoadData(Operator):
    """Logical node for load data operation

    Arguments:
        table_metainfo(DataFrameMetadata): table to load data into
        path(Path): file path from where we are loading data
    """

    def __init__(self, table_metainfo: DataFrameMetadata,
                 path: Path, children=None):
        super().__init__(OperatorType.LOGICALLOADDATA, children=children)
        self._table_metainfo = table_metainfo
        self._path = path

    @property
    def table_metainfo(self):
        return self._table_metainfo

    @property
    def path(self):
        return self._path

    def __str__(self):
        return 'LogicalLoadData(table: {}, path: {})'.format(
            self.table_metainfo, self.path)

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalLoadData):
            return False
        return (is_subtree_equal
                and self.table_metainfo == other.table_metainfo
                and self.path == other.path)
