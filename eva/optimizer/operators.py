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
from enum import IntEnum, auto
from typing import List

from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.expression.constant_value_expression import ConstantValueExpression
from eva.parser.create_statement import ColumnDefinition
from eva.parser.table_ref import TableRef
from eva.expression.abstract_expression import AbstractExpression
from eva.catalog.models.udf_io import UdfIO
from pathlib import Path


class OperatorType(IntEnum):
    """
    Manages enums for all the operators supported
    """
    DUMMY = auto()
    LOGICALGET = auto()
    LOGICALFILTER = auto()
    LOGICALPROJECT = auto()
    LOGICALINSERT = auto()
    LOGICALCREATE = auto()
    LOGICALCREATEUDF = auto()
    LOGICALLOADDATA = auto()
    LOGICALUPLOAD = auto()
    LOGICALQUERYDERIVEDGET = auto()
    LOGICALUNION = auto()
    LOGICALORDERBY = auto()
    LOGICALLIMIT = auto()
    LOGICALSAMPLE = auto()
    LOGICAL_CREATE_MATERIALIZED_VIEW = auto()
    LOGICALDELIMITER = auto()


class Operator:
    """Base class for logital plan of operators
    Arguments:
        op_type: {OperatorType} -- {the opr type held by this node}
        children: {List} -- {the list of operator children for this node}
    """

    def __init__(self, op_type: OperatorType, children=None):
        self._opr_type = op_type
        self._children = children or []

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, children):
        self._children = children

    @property
    def opr_type(self):
        return self._opr_type

    def append_child(self, child: 'Operator'):
        self.children.append(child)

    def clear_children(self):
        self.children = []

    def __str__(self) -> str:
        return '%s[%s](%s)' % (
            type(self).__name__, hex(id(self)),
            ', '.join('%s=%s' % item for item in vars(self).items())
        )

    def __eq__(self, other):
        is_subtree_equal = True
        if not isinstance(other, Operator):
            return False
        if len(self.children) != len(other.children):
            return False
        for child1, child2 in zip(self.children, other.children):
            is_subtree_equal = is_subtree_equal and (child1 == child2)
        return is_subtree_equal

    def is_logical(self):
        return self._opr_type < OperatorType.LOGICALDELIMITER

    def __hash__(self) -> int:
        return hash((self.opr_type, tuple(self.children)))

    def __copy__(self):
        # deepcopy the children
        cls = self.__class__
        result = cls.__new__(cls)
        for k, v in self.__dict__.items():
            if k == '_children':
                setattr(result, k, [])
            else:
                setattr(result, k, v)
        return result


class Dummy(Operator):
    '''
    Acts as a placeholder for matching any operator in optimizer.
    It track the group_id of the matching operator.
    '''

    def __init__(self, group_id: int):
        super().__init__(OperatorType.DUMMY, None)
        self.group_id = group_id

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.group_id))


class LogicalGet(Operator):
    def __init__(self,
                 video: TableRef,
                 dataset_metadata: DataFrameMetadata,
                 predicate: AbstractExpression = None,
                 target_list: List[AbstractExpression] = None,
                 children=None):
        self._video = video
        self._dataset_metadata = dataset_metadata
        self._predicate = predicate
        self._target_list = target_list or []
        super().__init__(OperatorType.LOGICALGET, children)

    @property
    def video(self):
        return self._video

    @property
    def dataset_metadata(self):
        return self._dataset_metadata

    @property
    def predicate(self):
        return self._predicate

    @predicate.setter
    def predicate(self, predicate):
        self._predicate = predicate

    @property
    def target_list(self):
        return self._target_list

    @target_list.setter
    def target_list(self, target_list):
        self._target_list = target_list

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalGet):
            return False
        return (is_subtree_equal
                and self.video == other.video
                and self.dataset_metadata == other.dataset_metadata
                and self.predicate == other.predicate
                and self.target_list == other.target_list)

    def __hash__(self) -> int:
        return hash((super().__hash__(),
                     self.video,
                     self.dataset_metadata,
                     self.predicate,
                     tuple(self.target_list)))


class LogicalQueryDerivedGet(Operator):
    def __init__(self,
                 predicate: AbstractExpression = None,
                 target_list: List[AbstractExpression] = None,
                 children: List = None):
        super().__init__(OperatorType.LOGICALQUERYDERIVEDGET,
                         children=children)
        # `TODO` We need to store the alias information here
        # We need construct the map using the target list of the
        # subquery to validate the overall query
        self.predicate = predicate
        self.target_list = target_list or []

    @property
    def predicate(self):
        return self._predicate

    @predicate.setter
    def predicate(self, predicate):
        self._predicate = predicate

    @property
    def target_list(self):
        return self._target_list

    @target_list.setter
    def target_list(self, target_list):
        self._target_list = target_list

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalQueryDerivedGet):
            return False
        return (is_subtree_equal
                and self.predicate == other.predicate
                and self.target_list == other.target_list)

    def __hash__(self) -> int:
        return hash((super().__hash__(),
                     self.predicate,
                     tuple(self.target_list)))


class LogicalFilter(Operator):
    def __init__(self, predicate: AbstractExpression, children=None):
        self._predicate = predicate
        super().__init__(OperatorType.LOGICALFILTER, children)

    @property
    def predicate(self):
        return self._predicate

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalFilter):
            return False
        return (is_subtree_equal
                and self.predicate == other.predicate)

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.predicate))


class LogicalProject(Operator):
    def __init__(self, target_list: List[AbstractExpression],
                 children=None):
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

    def __hash__(self) -> int:
        return hash((super().__hash__(), tuple(self.target_list)))


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

    def __hash__(self) -> int:
        return hash((super().__hash__(), tuple(self.orderby_list)))


class LogicalLimit(Operator):
    def __init__(self,
                 limit_count: ConstantValueExpression,
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

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.limit_count))


class LogicalSample(Operator):
    def __init__(self, sample_freq: ConstantValueExpression,
                 children: List = None):
        super().__init__(OperatorType.LOGICALSAMPLE, children)
        self._sample_freq = sample_freq

    @property
    def sample_freq(self):
        return self._sample_freq

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalSample):
            return False
        return (is_subtree_equal
                and self.sample_freq == other.sample_freq)

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.sample_freq))


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

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.all))


class LogicalInsert(Operator):
    """[Logical Node for Insert operation]

    Arguments:
        table_metainfo(DataFrameMetadata): table to intert data into
        column_list{List[AbstractExpression]}:
            [After binding annotated column_list]
        value_list{List[AbstractExpression]}:
            [value list to insert]
    """

    def __init__(self, table_metainfo: DataFrameMetadata,
                 column_list: List[AbstractExpression],
                 value_list: List[AbstractExpression],
                 children: List = None):
        super().__init__(OperatorType.LOGICALINSERT, children)
        self._table_metainfo = table_metainfo
        self._column_list = column_list
        self._value_list = value_list

    @property
    def table_metainfo(self):
        return self._table_metainfo

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
                and self.table_metainfo == other.table_metainfo
                and self.value_list == other.value_list
                and self.column_list == other.column_list)

    def __hash__(self) -> int:
        return hash((super().__hash__(),
                     self.table_metainfo,
                     tuple(self.value_list),
                     tuple(self.column_list)))


class LogicalCreate(Operator):
    """Logical node for create table operations

    Arguments:
        video {TableRef}: [video table that is to be created]
        column_list {List[ColumnDefinition]}:
        if_not_exists {bool}: [create table if exists]

    """

    def __init__(self, video: TableRef, column_list: List[ColumnDefinition],
                 if_not_exists: bool = False, children: List = None):
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

    def __hash__(self) -> int:
        return hash((super().__hash__(),
                     self.video,
                     tuple(self.column_list),
                     self.if_not_exists))


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
                 children: List = None):
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

    def __hash__(self) -> int:
        return hash((super().__hash__(),
                     self.name,
                     self.if_not_exists,
                     tuple(self.inputs),
                     tuple(self.outputs),
                     self.udf_type,
                     self.impl_path))


class LogicalLoadData(Operator):
    """Logical node for load data operation

    Arguments:
        table_metainfo(DataFrameMetadata): table to load data into
        path(Path): file path from where we are loading data
    """

    def __init__(self, table_metainfo: DataFrameMetadata,
                 path: Path,
                 column_list: List[AbstractExpression] = None,
                 file_options: dict = dict(), children: List = None):
        super().__init__(OperatorType.LOGICALLOADDATA, children=children)
        self._table_metainfo = table_metainfo
        self._path = path
        self._column_list = column_list or []
        self._file_options = file_options

    @property
    def table_metainfo(self):
        return self._table_metainfo

    @property
    def path(self):
        return self._path

    @property
    def column_list(self):
        return self._column_list

    @property
    def file_options(self):
        return self._file_options

    def __str__(self):
        return "LogicalLoadData(table: {}, path: {}, \
                column_list: {}, \
                file_options: {})".format(self.table_metainfo,
                                          self.path,
                                          self.column_list,
                                          self.file_options)

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalLoadData):
            return False
        return (is_subtree_equal
                and self.table_metainfo == other.table_metainfo
                and self.path == other.path
                and self.column_list == other.column_list
                and self.file_options == other.file_options)

    def __hash__(self) -> int:
        return hash((super().__hash__(),
                     self.table_metainfo,
                     self.path,
                     tuple(self.column_list),
                     frozenset(self.file_options.items())))


class LogicalUpload(Operator):
    """Logical node for upload operation

    Arguments:
        path(Path): file path (with prefix prepended) where
                    the data is uploaded
        video_blob(str): base64 encoded video string
    """

    def __init__(self, path: Path, video_blob: str, children=None):
        super().__init__(OperatorType.LOGICALUPLOAD, children=children)
        self._path = path
        self._video_blob = video_blob

    @property
    def path(self):
        return self._path

    @property
    def video_blob(self):
        return self._video_blob

    def __str__(self):
        return 'LogicalUpload(path: {} blob: {})'.format(
            self.path, "string of video blob")

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalUpload):
            return False
        return (is_subtree_equal
                and self.path == other.path
                and self.video_blob == other.video_blob)

    def __hash__(self) -> int:
        return hash((super().__hash__(),
                     self.path,
                     self.path,
                     self.video_blob))


class LogicalCreateMaterializedView(Operator):
    """Logical node for create materiaziled view operations
    Arguments:
        view {TableRef}: [view table that is to be created]
        col_list{List[ColumnDefinition]} -- column names in the view
        if_not_exists {bool}: [whether to override if view exists]
    """

    def __init__(self, view: TableRef, col_list: List[ColumnDefinition],
                 if_not_exists: bool = False, children=None):
        super().__init__(OperatorType.LOGICAL_CREATE_MATERIALIZED_VIEW,
                         children)
        self._view = view
        self._col_list = col_list
        self._if_not_exists = if_not_exists

    @property
    def view(self):
        return self._view

    @property
    def if_not_exists(self):
        return self._if_not_exists

    @property
    def col_list(self):
        return self._col_list

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalCreateMaterializedView):
            return False
        return (is_subtree_equal
                and self.view == other.view
                and self.col_list == other.col_list
                and self.if_not_exists == other.if_not_exists)

    def __hash__(self) -> int:
        return hash((super().__hash__(),
                     self.view,
                     tuple(self.col_list),
                     self.if_not_exists))
