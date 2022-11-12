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
from enum import IntEnum, auto
from pathlib import Path
from typing import List

from eva.catalog.models.df_column import DataFrameColumn
from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.catalog.models.udf_io import UdfIO
from eva.expression.abstract_expression import AbstractExpression
from eva.expression.constant_value_expression import ConstantValueExpression
from eva.parser.alias import Alias
from eva.parser.create_statement import ColumnDefinition
from eva.parser.table_ref import TableInfo, TableRef
from eva.parser.types import JoinType, ShowType


class OperatorType(IntEnum):
    """
    Manages enums for all the operators supported
    """

    DUMMY = auto()
    LOGICALEXCHANGE = auto()
    LOGICALGET = auto()
    LOGICALFILTER = auto()
    LOGICALPROJECT = auto()
    LOGICALINSERT = auto()
    LOGICALCREATE = auto()
    LOGICALRENAME = auto()
    LOGICALDROP = auto()
    LOGICALCREATEUDF = auto()
    LOGICALLOADDATA = auto()
    LOGICALUPLOAD = auto()
    LOGICALQUERYDERIVEDGET = auto()
    LOGICALUNION = auto()
    LOGICALGROUPBY = auto()
    LOGICALORDERBY = auto()
    LOGICALLIMIT = auto()
    LOGICALSAMPLE = auto()
    LOGICALJOIN = auto()
    LOGICALFUNCTIONSCAN = auto()
    LOGICAL_CREATE_MATERIALIZED_VIEW = auto()
    LOGICAL_SHOW = auto()
    LOGICALDROPUDF = auto()
    LOGICALEXPLAIN = auto()
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

    def append_child(self, child: "Operator"):
        self.children.append(child)

    def clear_children(self):
        self.children = []

    def __str__(self) -> str:
        return "%s[%s](%s)" % (
            type(self).__name__,
            hex(id(self)),
            ", ".join("%s=%s" % item for item in vars(self).items()),
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
            if k == "_children":
                setattr(result, k, [])
            else:
                setattr(result, k, v)
        return result


class Dummy(Operator):
    """
    Acts as a placeholder for matching any operator in optimizer.
    It track the group_id of the matching operator.
    """

    def __init__(self, group_id: int):
        super().__init__(OperatorType.DUMMY, None)
        self.group_id = group_id

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.group_id))


class LogicalGet(Operator):
    def __init__(
        self,
        video: TableRef,
        dataset_metadata: DataFrameMetadata,
        alias: str,
        predicate: AbstractExpression = None,
        target_list: List[AbstractExpression] = None,
        sampling_rate: int = None,
        children=None,
    ):
        self._video = video
        self._dataset_metadata = dataset_metadata
        self._alias = alias
        self._predicate = predicate
        self._target_list = target_list
        self._sampling_rate = sampling_rate
        super().__init__(OperatorType.LOGICALGET, children)

    @property
    def video(self):
        return self._video

    @property
    def dataset_metadata(self):
        return self._dataset_metadata

    @property
    def alias(self):
        return self._alias

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

    @property
    def sampling_rate(self):
        return self._sampling_rate

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalGet):
            return False
        return (
            is_subtree_equal
            and self.video == other.video
            and self.dataset_metadata == other.dataset_metadata
            and self.alias == other.alias
            and self.predicate == other.predicate
            and self.target_list == other.target_list
            and self.sampling_rate == other.sampling_rate
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.alias,
                self.video,
                self.dataset_metadata,
                self.predicate,
                tuple(self.target_list or []),
                self.sampling_rate,
            )
        )


class LogicalQueryDerivedGet(Operator):
    def __init__(
        self,
        alias: str,
        predicate: AbstractExpression = None,
        target_list: List[AbstractExpression] = None,
        children: List = None,
    ):
        super().__init__(OperatorType.LOGICALQUERYDERIVEDGET, children=children)
        self._alias = alias
        self.predicate = predicate
        self.target_list = target_list or []

    @property
    def alias(self):
        return self._alias

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalQueryDerivedGet):
            return False
        return (
            is_subtree_equal
            and self.predicate == other.predicate
            and self.target_list == other.target_list
            and self.alias == other.alias
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.alias,
                self.predicate,
                tuple(self.target_list),
            )
        )


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
        return is_subtree_equal and self.predicate == other.predicate

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.predicate))


class LogicalProject(Operator):
    def __init__(self, target_list: List[AbstractExpression], children=None):
        super().__init__(OperatorType.LOGICALPROJECT, children)
        self._target_list = target_list

    @property
    def target_list(self):
        return self._target_list

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalProject):
            return False
        return is_subtree_equal and self.target_list == other.target_list

    def __hash__(self) -> int:
        return hash((super().__hash__(), tuple(self.target_list)))


class LogicalGroupBy(Operator):
    def __init__(self, groupby_clause: ConstantValueExpression, children: List = None):
        super().__init__(OperatorType.LOGICALGROUPBY, children)
        self._groupby_clause = groupby_clause

    @property
    def groupby_clause(self):
        return self._groupby_clause

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalGroupBy):
            return False
        return is_subtree_equal and self.groupby_clause == other.groupby_clause

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.groupby_clause))


class LogicalOrderBy(Operator):
    def __init__(self, orderby_list: List, children: List = None):
        super().__init__(OperatorType.LOGICALORDERBY, children)
        self._orderby_list = orderby_list

    @property
    def orderby_list(self):
        return self._orderby_list

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalOrderBy):
            return False
        return is_subtree_equal and self.orderby_list == other.orderby_list

    def __hash__(self) -> int:
        return hash((super().__hash__(), tuple(self.orderby_list)))


class LogicalLimit(Operator):
    def __init__(self, limit_count: ConstantValueExpression, children: List = None):
        super().__init__(OperatorType.LOGICALLIMIT, children)
        self._limit_count = limit_count

    @property
    def limit_count(self):
        return self._limit_count

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalLimit):
            return False
        return is_subtree_equal and self.limit_count == other.limit_count

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.limit_count))


class LogicalSample(Operator):
    def __init__(self, sample_freq: ConstantValueExpression, children: List = None):
        super().__init__(OperatorType.LOGICALSAMPLE, children)
        self._sample_freq = sample_freq

    @property
    def sample_freq(self):
        return self._sample_freq

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalSample):
            return False
        return is_subtree_equal and self.sample_freq == other.sample_freq

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
        return is_subtree_equal and self.all == other.all

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

    def __init__(
        self,
        table_metainfo: DataFrameMetadata,
        column_list: List[AbstractExpression],
        value_list: List[AbstractExpression],
        children: List = None,
    ):
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
        return (
            is_subtree_equal
            and self.table_metainfo == other.table_metainfo
            and self.value_list == other.value_list
            and self.column_list == other.column_list
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.table_metainfo,
                tuple(self.value_list),
                tuple(self.column_list),
            )
        )


class LogicalCreate(Operator):
    """Logical node for create table operations

    Arguments:
        video {TableRef}: [video table that is to be created]
        column_list {List[ColumnDefinition]}:
        if_not_exists {bool}: [create table if exists]

    """

    def __init__(
        self,
        video: TableRef,
        column_list: List[ColumnDefinition],
        if_not_exists: bool = False,
        children: List = None,
    ):
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
        return (
            is_subtree_equal
            and self.video == other.video
            and self.column_list == other.column_list
            and self.if_not_exists == other.if_not_exists
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.video,
                tuple(self.column_list),
                self.if_not_exists,
            )
        )


class LogicalRename(Operator):
    """Logical node for rename table operations

    Arguments:
        old_table {TableRef}: [old table that is to be renamed]
        new_name {TableInfo}: [new name for the old table]
    """

    def __init__(self, old_table_ref: TableRef, new_name: TableInfo, children=None):
        super().__init__(OperatorType.LOGICALRENAME, children)
        self._new_name = new_name
        self._old_table_ref = old_table_ref

    @property
    def new_name(self):
        return self._new_name

    @property
    def old_table_ref(self):
        return self._old_table_ref

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalRename):
            return False
        return (
            is_subtree_equal
            and self._new_name == other._new_name
            and self._old_table_ref == other._old_table_ref
        )

    def __hash__(self) -> int:
        return hash((super().__hash__(), self._new_name, self._old_table_ref))


class LogicalDrop(Operator):
    """
    Logical node for drop table operations
    """

    def __init__(self, table_refs: List[TableRef], if_exists: bool, children=None):
        super().__init__(OperatorType.LOGICALDROP, children)
        self._table_refs = table_refs
        self._if_exists = if_exists

    @property
    def table_refs(self):
        return self._table_refs

    @property
    def if_exists(self):
        return self._if_exists

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalDrop):
            return False
        return (
            is_subtree_equal
            and self.table_refs == other.table_refs
            and self.if_exists == other.if_exists
        )

    def __hash__(self) -> int:
        return hash((super().__hash__(), tuple(self._table_refs), self._if_exists))


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

    def __init__(
        self,
        name: str,
        if_not_exists: bool,
        inputs: List[UdfIO],
        outputs: List[UdfIO],
        impl_path: Path,
        udf_type: str = None,
        children: List = None,
    ):
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
        return (
            is_subtree_equal
            and self.name == other.name
            and self.if_not_exists == other.if_not_exists
            and self.inputs == other.inputs
            and self.outputs == other.outputs
            and self.udf_type == other.udf_type
            and self.impl_path == other.impl_path
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.name,
                self.if_not_exists,
                tuple(self.inputs),
                tuple(self.outputs),
                self.udf_type,
                self.impl_path,
            )
        )


class LogicalDropUDF(Operator):
    """
    Logical node for DROP UDF operations

    Attributes:
        name: str
            UDF name provided by the user
        if_exists: bool
            if false, throws an error when no UDF with name exists
            else logs a warning
    """

    def __init__(self, name: str, if_exists: bool, children: List = None):
        super().__init__(OperatorType.LOGICALDROPUDF, children)
        self._name = name
        self._if_exists = if_exists

    @property
    def name(self):
        return self._name

    @property
    def if_exists(self):
        return self._if_exists

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalDropUDF):
            return False
        return (
            is_subtree_equal
            and self.name == other.name
            and self.if_exists == other.if_exists
        )

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.name, self.if_exists))


class LogicalLoadData(Operator):
    """Logical node for load data operation

    Arguments:
        table_metainfo(DataFrameMetadata): table to load data into
        path(Path): file path from where we are loading data
    """

    def __init__(
        self,
        table_metainfo: DataFrameMetadata,
        path: Path,
        column_list: List[AbstractExpression] = None,
        file_options: dict = dict(),
        children: List = None,
    ):
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
                file_options: {})".format(
            self.table_metainfo, self.path, self.column_list, self.file_options
        )

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalLoadData):
            return False
        return (
            is_subtree_equal
            and self.table_metainfo == other.table_metainfo
            and self.path == other.path
            and self.column_list == other.column_list
            and self.file_options == other.file_options
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.table_metainfo,
                self.path,
                tuple(self.column_list),
                frozenset(self.file_options.items()),
            )
        )


class LogicalUpload(Operator):
    """Logical node for upload operation

    Arguments:
        path(Path): file path (with prefix prepended) where
                    the data is uploaded
        video_blob(str): base64 encoded video string
    """

    def __init__(
        self,
        path: Path,
        video_blob: str,
        table_metainfo: DataFrameMetadata,
        column_list: List[AbstractExpression] = None,
        file_options: dict = dict(),
        children: List = None,
    ):
        super().__init__(OperatorType.LOGICALUPLOAD, children=children)
        self._path = path
        self._video_blob = video_blob
        self._table_metainfo = table_metainfo
        self._column_list = column_list or []
        self._file_options = file_options

    @property
    def path(self):
        return self._path

    @property
    def video_blob(self):
        return self._video_blob

    @property
    def table_metainfo(self):
        return self._table_metainfo

    @property
    def column_list(self):
        return self._column_list

    @property
    def file_options(self):
        return self._file_options

    def __str__(self):
        return "LogicalUpload(path: {}, \
                blob: {}, \
                table: {}, \
                column_list: {}, \
                file_options: {})".format(
            self.path,
            "string of video blob",
            self.table_metainfo,
            self.column_list,
            self.file_options,
        )

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalUpload):
            return False
        return (
            is_subtree_equal
            and self.path == other.path
            and self.video_blob == other.video_blob
            and self.table_metainfo == other.table_metainfo
            and self.column_list == other.column_list
            and self.file_options == other.file_options
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.path,
                self.video_blob,
                self.table_metainfo,
                tuple(self.column_list),
                frozenset(self.file_options.items()),
            )
        )


class LogicalFunctionScan(Operator):
    """
    Logical node for function table scans

    Attributes:
        func_expr: AbstractExpression
            function_expression that yield a table like output
    """

    def __init__(
        self,
        func_expr: AbstractExpression,
        alias: Alias,
        do_unnest: bool = False,
        children: List = None,
    ):
        super().__init__(OperatorType.LOGICALFUNCTIONSCAN, children)
        self._func_expr = func_expr
        self._do_unnest = do_unnest
        self._alias = alias

    @property
    def alias(self):
        return self._alias

    @property
    def func_expr(self):
        return self._func_expr

    @property
    def do_unnest(self):
        return self._do_unnest

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalFunctionScan):
            return False
        return (
            is_subtree_equal
            and self.func_expr == other.func_expr
            and self.do_unnest == other.do_unnest
            and self.alias == other.alias
        )

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.func_expr))


class LogicalJoin(Operator):
    """
    Logical node for join operators

    Attributes:
        join_type: JoinType
            Join type provided by the user - Lateral, Inner, Outer
        join_predicate: AbstractExpression
            condition/predicate expression used to join the tables
    """

    def __init__(
        self,
        join_type: JoinType,
        join_predicate: AbstractExpression = None,
        left_keys: List[DataFrameColumn] = None,
        right_keys: List[DataFrameColumn] = None,
        children: List = None,
    ):
        super().__init__(OperatorType.LOGICALJOIN, children)
        self._join_type = join_type
        self._join_predicate = join_predicate
        self._left_keys = left_keys
        self._right_keys = right_keys
        self._join_project = []

    @property
    def join_type(self):
        return self._join_type

    @property
    def join_predicate(self):
        return self._join_predicate

    @join_predicate.setter
    def join_predicate(self, predicate):
        self._join_predicate = predicate

    @property
    def left_keys(self):
        return self._left_keys

    @left_keys.setter
    def left_keys(self, keys):
        self._left_key = keys

    @property
    def right_keys(self):
        return self._right_keys

    @right_keys.setter
    def right_keys(self, keys):
        self._right_keys = keys

    @property
    def join_project(self):
        return self._join_project

    @join_project.setter
    def join_project(self, join_project):
        self._target_list = join_project

    def lhs(self):
        return self.children[0]

    def rhs(self):
        return self.children[1]

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalJoin):
            return False
        return (
            is_subtree_equal
            and self.join_type == other.join_type
            and self.join_predicate == other.join_predicate
            and self.left_keys == other.left_keys
            and self.right_keys == other.right_keys
            and self.join_project == other.join_project
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.join_type,
                self.join_predicate,
                self.left_keys,
                self.right_keys,
                tuple(self.join_project),
            )
        )


class LogicalCreateMaterializedView(Operator):
    """Logical node for create materiaziled view operations
    Arguments:
        view {TableRef}: [view table that is to be created]
        col_list{List[ColumnDefinition]} -- column names in the view
        if_not_exists {bool}: [whether to override if view exists]
    """

    def __init__(
        self,
        view: TableRef,
        col_list: List[ColumnDefinition],
        if_not_exists: bool = False,
        children=None,
    ):
        super().__init__(OperatorType.LOGICAL_CREATE_MATERIALIZED_VIEW, children)
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
        return (
            is_subtree_equal
            and self.view == other.view
            and self.col_list == other.col_list
            and self.if_not_exists == other.if_not_exists
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.view,
                tuple(self.col_list),
                self.if_not_exists,
            )
        )


class LogicalShow(Operator):
    def __init__(self, show_type: ShowType, children: List = None):
        super().__init__(OperatorType.LOGICAL_SHOW, children)
        self._show_type = show_type

    @property
    def show_type(self):
        return self._show_type

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalShow):
            return False
        return is_subtree_equal and self.show_type == other.show_type

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.show_type))


class LogicalExchange(Operator):
    def __init__(self, children=None):
        super().__init__(OperatorType.LOGICALEXCHANGE, children)

    def __eq__(self, other):
        if not isinstance(other, LogicalExchange):
            return False
        return True

    def __hash__(self) -> int:
        return super().__hash__()


class LogicalExplain(Operator):
    def __init__(self, children: List = None):
        super().__init__(OperatorType.LOGICALEXPLAIN, children)
        assert len(children) == 1, "EXPLAIN command only takes one child"
        self._explainable_opr = children[0]

    @property
    def explainable_opr(self):
        return self._explainable_opr

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalExplain):
            return False
        return is_subtree_equal and self._explainable_opr == other.explainable_opr

    def __hash__(self) -> int:
        return hash((super().__hash__(), self._explainable_opr))
