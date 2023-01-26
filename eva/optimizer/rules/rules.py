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
from __future__ import annotations

from typing import TYPE_CHECKING

from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.catalog_type import TableType
from eva.catalog.catalog_utils import is_video_table
from eva.expression.expression_utils import conjuction_list_to_expression_tree
from eva.expression.function_expression import FunctionExpression
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.optimizer.optimizer_utils import (
    extract_equi_join_keys,
    extract_pushdown_predicate,
    extract_pushdown_predicate_for_alias,
)
from eva.optimizer.rules.pattern import Pattern
from eva.optimizer.rules.rules_base import Promise, Rule, RuleType
from eva.parser.types import JoinType, ParserOrderBySortType
from eva.plan_nodes.apply_and_merge_plan import ApplyAndMergePlan
from eva.plan_nodes.create_mat_view_plan import CreateMaterializedViewPlan
from eva.plan_nodes.explain_plan import ExplainPlan
from eva.plan_nodes.hash_join_build_plan import HashJoinBuildPlan
from eva.plan_nodes.predicate_plan import PredicatePlan
from eva.plan_nodes.project_plan import ProjectPlan
from eva.plan_nodes.show_info_plan import ShowInfoPlan

if TYPE_CHECKING:
    from eva.optimizer.optimizer_context import OptimizerContext

from eva.configuration.configuration_manager import ConfigurationManager
from eva.optimizer.operators import (
    Dummy,
    LogicalApplyAndMerge,
    LogicalCreate,
    LogicalCreateIndex,
    LogicalCreateMaterializedView,
    LogicalCreateUDF,
    LogicalDrop,
    LogicalDropUDF,
    LogicalExplain,
    LogicalFaissIndexScan,
    LogicalFilter,
    LogicalFunctionScan,
    LogicalGet,
    LogicalGroupBy,
    LogicalInsert,
    LogicalJoin,
    LogicalLimit,
    LogicalLoadData,
    LogicalOrderBy,
    LogicalProject,
    LogicalQueryDerivedGet,
    LogicalRename,
    LogicalSample,
    LogicalShow,
    LogicalUnion,
    LogicalUpload,
    Operator,
    OperatorType,
)
from eva.plan_nodes.create_index_plan import CreateIndexPlan
from eva.plan_nodes.create_plan import CreatePlan
from eva.plan_nodes.create_udf_plan import CreateUDFPlan
from eva.plan_nodes.drop_plan import DropPlan
from eva.plan_nodes.drop_udf_plan import DropUDFPlan
from eva.plan_nodes.faiss_index_scan_plan import FaissIndexScanPlan
from eva.plan_nodes.function_scan_plan import FunctionScanPlan
from eva.plan_nodes.groupby_plan import GroupByPlan
from eva.plan_nodes.hash_join_probe_plan import HashJoinProbePlan
from eva.plan_nodes.insert_plan import InsertPlan
from eva.plan_nodes.lateral_join_plan import LateralJoinPlan
from eva.plan_nodes.limit_plan import LimitPlan
from eva.plan_nodes.load_data_plan import LoadDataPlan
from eva.plan_nodes.orderby_plan import OrderByPlan
from eva.plan_nodes.rename_plan import RenamePlan
from eva.plan_nodes.sample_plan import SamplePlan
from eva.plan_nodes.seq_scan_plan import SeqScanPlan
from eva.plan_nodes.storage_plan import StoragePlan
from eva.plan_nodes.union_plan import UnionPlan
from eva.plan_nodes.upload_plan import UploadPlan

##############################################
# REWRITE RULES START


class EmbedFilterIntoGet(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALFILTER)
        pattern.append_child(Pattern(OperatorType.LOGICALGET))
        super().__init__(RuleType.EMBED_FILTER_INTO_GET, pattern)

    def promise(self):
        return Promise.EMBED_FILTER_INTO_GET

    def check(self, before: LogicalFilter, context: OptimizerContext):
        # System supports predicate pushdown only while reading video data
        predicate = before.predicate
        lget: LogicalGet = before.children[0]
        if predicate and is_video_table(lget.table_obj):
            # System only supports pushing basic range predicates on id
            video_alias = lget.video.alias
            col_alias = f"{video_alias}.id"
            pushdown_pred, _ = extract_pushdown_predicate(predicate, col_alias)
            if pushdown_pred:
                return True
        return False

    def apply(self, before: LogicalFilter, context: OptimizerContext):
        predicate = before.predicate
        lget = before.children[0]
        # System only supports pushing basic range predicates on id
        video_alias = lget.video.alias
        col_alias = f"{video_alias}.id"
        pushdown_pred, unsupported_pred = extract_pushdown_predicate(
            predicate, col_alias
        )
        if pushdown_pred:
            new_get_opr = LogicalGet(
                lget.video,
                lget.table_obj,
                alias=lget.alias,
                predicate=pushdown_pred,
                target_list=lget.target_list,
                sampling_rate=lget.sampling_rate,
                children=lget.children,
            )
            if unsupported_pred:
                unsupported_opr = LogicalFilter(unsupported_pred)
                unsupported_opr.append_child(new_get_opr)
                new_get_opr = unsupported_opr
            yield new_get_opr
        else:
            yield before


class EmbedSampleIntoGet(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALSAMPLE)
        pattern.append_child(Pattern(OperatorType.LOGICALGET))
        super().__init__(RuleType.EMBED_SAMPLE_INTO_GET, pattern)

    def promise(self):
        return Promise.EMBED_SAMPLE_INTO_GET

    def check(self, before: LogicalSample, context: OptimizerContext):
        # System supports sample pushdown only while reading video data
        lget: LogicalGet = before.children[0]
        if lget.table_obj.table_type == TableType.VIDEO_DATA:
            return True
        return False

    def apply(self, before: LogicalSample, context: OptimizerContext):
        sample_freq = before.sample_freq.value
        lget: LogicalGet = before.children[0]
        new_get_opr = LogicalGet(
            lget.video,
            lget.table_obj,
            alias=lget.alias,
            predicate=lget.predicate,
            target_list=lget.target_list,
            sampling_rate=sample_freq,
            children=lget.children,
        )
        yield new_get_opr


class EmbedProjectIntoGet(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALPROJECT)
        pattern.append_child(Pattern(OperatorType.LOGICALGET))
        super().__init__(RuleType.EMBED_PROJECT_INTO_GET, pattern)

    def promise(self):
        return Promise.EMBED_PROJECT_INTO_GET

    def check(self, before: Operator, context: OptimizerContext):
        # nothing else to check if logical match found return true
        return True

    def apply(self, before: LogicalProject, context: OptimizerContext):
        target_list = before.target_list
        lget = before.children[0]
        new_get_opr = LogicalGet(
            lget.video,
            lget.table_obj,
            alias=lget.alias,
            predicate=lget.predicate,
            target_list=target_list,
            sampling_rate=lget.sampling_rate,
            children=lget.children,
        )

        yield new_get_opr


# For nested queries


class EmbedFilterIntoDerivedGet(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALFILTER)
        pattern_get = Pattern(OperatorType.LOGICALQUERYDERIVEDGET)
        pattern_get.append_child(Pattern(OperatorType.DUMMY))
        pattern.append_child(pattern_get)
        super().__init__(RuleType.EMBED_FILTER_INTO_DERIVED_GET, pattern)

    def promise(self):
        return Promise.EMBED_FILTER_INTO_DERIVED_GET

    def check(self, before: Operator, context: OptimizerContext):
        # nothing else to check if logical match found return true
        return True

    def apply(self, before: LogicalFilter, context: OptimizerContext):
        predicate = before.predicate
        ld_get = before.children[0]
        new_opr = LogicalQueryDerivedGet(
            alias=ld_get.alias,
            predicate=predicate,
            target_list=ld_get.target_list,
            children=ld_get.children,
        )
        yield new_opr


class EmbedProjectIntoDerivedGet(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALPROJECT)
        pattern_get = Pattern(OperatorType.LOGICALQUERYDERIVEDGET)
        pattern_get.append_child(Pattern(OperatorType.DUMMY))
        pattern.append_child(pattern_get)
        super().__init__(RuleType.EMBED_PROJECT_INTO_DERIVED_GET, pattern)

    def promise(self):
        return Promise.EMBED_PROJECT_INTO_DERIVED_GET

    def check(self, before: Operator, context: OptimizerContext):
        # nothing else to check if logical match found return true
        return True

    def apply(self, before: LogicalProject, context: OptimizerContext):
        target_list = before.target_list
        ld_get = before.children[0]
        new_opr = LogicalQueryDerivedGet(
            alias=ld_get.alias,
            predicate=ld_get.predicate,
            target_list=target_list,
            children=ld_get.children,
        )
        yield new_opr


# Join Queries
class PushDownFilterThroughJoin(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALFILTER)
        pattern_join = Pattern(OperatorType.LOGICALJOIN)
        pattern_join.append_child(Pattern(OperatorType.DUMMY))
        pattern_join.append_child(Pattern(OperatorType.DUMMY))
        pattern.append_child(pattern_join)
        super().__init__(RuleType.PUSHDOWN_FILTER_THROUGH_JOIN, pattern)

    def promise(self):
        return Promise.PUSHDOWN_FILTER_THROUGH_JOIN

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalFilter, context: OptimizerContext):
        predicate = before.predicate
        join: LogicalJoin = before.children[0]
        left: Dummy = join.children[0]
        right: Dummy = join.children[1]

        new_join_node = LogicalJoin(
            join.join_type,
            join.join_predicate,
            join.left_keys,
            join.right_keys,
        )
        left_group_aliases = context.memo.get_group_by_id(left.group_id).aliases
        right_group_aliases = context.memo.get_group_by_id(right.group_id).aliases

        left_pushdown_pred, rem_pred = extract_pushdown_predicate_for_alias(
            predicate, left_group_aliases
        )
        right_pushdown_pred, rem_pred = extract_pushdown_predicate_for_alias(
            rem_pred, right_group_aliases
        )

        if left_pushdown_pred:
            left_filter = LogicalFilter(predicate=left_pushdown_pred)
            left_filter.append_child(left)
            new_join_node.append_child(left_filter)
        else:
            new_join_node.append_child(left)

        if right_pushdown_pred:
            right_filter = LogicalFilter(predicate=right_pushdown_pred)
            right_filter.append_child(right)
            new_join_node.append_child(right_filter)
        else:
            new_join_node.append_child(right)

        if rem_pred:
            new_join_node.join_predicate = conjuction_list_to_expression_tree(
                [rem_pred, new_join_node.join_predicate]
            )

        yield new_join_node


class XformLateralJoinToLinearFlow(Rule):
    """If the inner node of a lateral join is a function-valued expression, we
    eliminate the join node and make the inner node the parent of the outer node. This
    produces a linear #data flow path. Because this scenario is common in our system,
    we chose to explicitly convert it to a linear flow, which simplifies the
    implementation of other optimizations such as UDF reuse and parallelized plans by
    removing the join."""

    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALJOIN)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        pattern.append_child(Pattern(OperatorType.LOGICALFUNCTIONSCAN))
        super().__init__(RuleType.XFORM_LATERAL_JOIN_TO_LINEAR_FLOW, pattern)

    def promise(self):
        return Promise.XFORM_LATERAL_JOIN_TO_LINEAR_FLOW

    def check(self, before: LogicalJoin, context: OptimizerContext):
        if before.join_type == JoinType.LATERAL_JOIN:
            if before.join_predicate is None and not before.join_project:
                return True
        return False

    def apply(self, before: LogicalJoin, context: OptimizerContext):
        #     LogicalJoin(Lateral)              LogicalApplyAndMerge
        #     /           \                 ->       |
        #    A        LogicalFunctionScan            A

        A: Dummy = before.children[0]
        logical_func_scan: LogicalFunctionScan = before.children[1]
        logical_apply_merge = LogicalApplyAndMerge(
            logical_func_scan.func_expr,
            logical_func_scan.alias,
            logical_func_scan.do_unnest,
        )
        logical_apply_merge.append_child(A)
        yield logical_apply_merge


class PushDownFilterThroughApplyAndMerge(Rule):
    """If it is feasible to partially or fully push the predicate contained within the
    logical filter through the ApplyAndMerge operator, we should do so. This is often
    beneficial, for instance, in order to prevent decoding additional frames beyond
    those that satisfy the predicate.
    Eg:

    Filter(id < 10 and func.label = 'car')           Filter(func.label = 'car')
            |                                                   |
        ApplyAndMerge(func)                  ->          ApplyAndMerge(func)
            |                                                   |
            A                                            Filter(id < 10)
                                                                |
                                                                A

    """

    def __init__(self):
        appply_merge_pattern = Pattern(OperatorType.LOGICAL_APPLY_AND_MERGE)
        appply_merge_pattern.append_child(Pattern(OperatorType.DUMMY))
        pattern = Pattern(OperatorType.LOGICALFILTER)
        pattern.append_child(appply_merge_pattern)
        super().__init__(RuleType.PUSHDOWN_FILTER_THROUGH_APPLY_AND_MERGE, pattern)

    def promise(self):
        return Promise.PUSHDOWN_FILTER_THROUGH_APPLY_AND_MERGE

    def check(self, before: LogicalFilter, context: OptimizerContext):
        return True

    def apply(self, before: LogicalFilter, context: OptimizerContext):
        A: Dummy = before.children[0].children[0]
        apply_and_merge: LogicalApplyAndMerge = before.children[0]
        aliases = context.memo.get_group_by_id(A.group_id).aliases
        predicate = before.predicate
        pushdown_pred, rem_pred = extract_pushdown_predicate_for_alias(
            predicate, aliases
        )

        # if we find a feasible pushdown predicate, add a new filter node between
        # ApplyAndMerge and Dummy
        if pushdown_pred:
            pushdown_filter = LogicalFilter(predicate=pushdown_pred)
            pushdown_filter.append_child(A)
            apply_and_merge.children = [pushdown_filter]

        # If we have partial predicate make it the root
        root_node = apply_and_merge
        if rem_pred:
            root_node = LogicalFilter(predicate=rem_pred)
            root_node.append_child(apply_and_merge)

        yield root_node


class CombineSimilarityOrderByAndLimitToFaissIndexScan(Rule):
    """
    This rule currently rewrites Order By + Limit to a Faiss index scan.
    Because Faiss index only works for similarity search, the rule will
    only be applied when the Order By is on Similarity expression. For
    simplicity, we also only enable this rule when the Similarity expression
    applies to the full table. Predicated query will yield incorrect results
    if we use an index scan.

    Limit(10)
        |
    OrderBy(func)        ->        IndexScan(10)
        |                               |
        A                               A
    """

    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALLIMIT)
        orderby_pattern = Pattern(OperatorType.LOGICALORDERBY)
        orderby_pattern.append_child(Pattern(OperatorType.DUMMY))
        pattern.append_child(orderby_pattern)
        super().__init__(
            RuleType.COMBINE_SIMILARITY_ORDERBY_AND_LIMIT_TO_FAISS_INDEX_SCAN, pattern
        )

        # Entries populate after rule egibility validation.
        self._index_catalog_entry = None
        self._query_func_expr = None

    def promise(self):
        return Promise.COMBINE_SIMILARITY_ORDERBY_AND_LIMIT_TO_FAISS_INDEX_SCAN

    def check(self, before: LogicalLimit, context: OptimizerContext):
        return True

    def apply(self, before: LogicalLimit, context: OptimizerContext):
        catalog_manager = CatalogManager()

        # Get corresponding nodes.
        limit_node = before
        orderby_node = before.children[0]
        sub_tree_root = orderby_node.children[0]

        # Check if predicate exists on table.
        def _exists_predicate(opr):
            if isinstance(opr, LogicalFilter):
                return True
            elif isinstance(opr, LogicalGet):
                return opr.predicate is not None
            elif isinstance(opr, LogicalQueryDerivedGet):
                return opr.predicate is not None
            exists_predicate = False
            for child in opr.children:
                exists_predicate |= _exists_predicate(child)
            return exists_predicate

        if _exists_predicate(sub_tree_root.opr):
            return

        # Check if orderby runs on similarity expression.
        # Current optimization will only accept Similarity expression.
        func_orderby_expr = None
        for column, sort_type in orderby_node.orderby_list:
            if (
                isinstance(column, FunctionExpression)
                and sort_type == ParserOrderBySortType.ASC
            ):
                func_orderby_expr = column
        if not func_orderby_expr or func_orderby_expr.name != "Similarity":
            return

        # Check if there exists an index on table and column.
        query_func_expr, base_func_expr = func_orderby_expr.children

        # Get table and column of orderby.
        tv_expr = base_func_expr
        while not isinstance(tv_expr, TupleValueExpression):
            tv_expr = tv_expr.children[0]

        # Get column catalog entry and udf_signature.
        column_catalog_entry = tv_expr.col_object
        udf_signature = (
            None
            if isinstance(base_func_expr, TupleValueExpression)
            else base_func_expr.signature()
        )

        # Get index catalog. Check if an index exists for matching
        # udf signature and table columns.
        index_catalog_entry = (
            catalog_manager.get_index_catalog_entry_by_column_and_udf_signature(
                column_catalog_entry, udf_signature
            )
        )
        if not index_catalog_entry:
            return

        # Construct the Faiss index scan plan.
        faiss_index_scan_node = LogicalFaissIndexScan(
            index_catalog_entry.name,
            limit_node.limit_count,
            query_func_expr,
        )
        for child in orderby_node.children:
            faiss_index_scan_node.append_child(child)
        yield faiss_index_scan_node


# REWRITE RULES END
##############################################

##############################################
# LOGICAL RULES START


class LogicalInnerJoinCommutativity(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALJOIN)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_INNER_JOIN_COMMUTATIVITY, pattern)

    def promise(self):
        return Promise.LOGICAL_INNER_JOIN_COMMUTATIVITY

    def check(self, before: LogicalJoin, context: OptimizerContext):
        # has to be an inner join
        return before.join_type == JoinType.INNER_JOIN

    def apply(self, before: LogicalJoin, context: OptimizerContext):
        #     LogicalJoin(Inner)            LogicalJoin(Inner)
        #     /           \        ->       /               \
        #    A             B               B                A

        new_join = LogicalJoin(before.join_type, before.join_predicate)
        new_join.append_child(before.rhs())
        new_join.append_child(before.lhs())
        yield new_join


# LOGICAL RULES END
##############################################


##############################################
# IMPLEMENTATION RULES START


class LogicalCreateToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALCREATE)
        super().__init__(RuleType.LOGICAL_CREATE_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_CREATE_TO_PHYSICAL

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalCreate, context: OptimizerContext):
        after = CreatePlan(before.video, before.column_list, before.if_not_exists)
        yield after


class LogicalRenameToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALRENAME)
        super().__init__(RuleType.LOGICAL_RENAME_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_RENAME_TO_PHYSICAL

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalRename, context: OptimizerContext):
        after = RenamePlan(before.old_table_ref, before.new_name)
        yield after


class LogicalDropToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALDROP)
        super().__init__(RuleType.LOGICAL_DROP_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_DROP_TO_PHYSICAL

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalDrop, context: OptimizerContext):
        after = DropPlan(before.table_infos, before.if_exists)
        yield after


class LogicalCreateUDFToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALCREATEUDF)
        super().__init__(RuleType.LOGICAL_CREATE_UDF_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_CREATE_UDF_TO_PHYSICAL

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalCreateUDF, context: OptimizerContext):
        after = CreateUDFPlan(
            before.name,
            before.if_not_exists,
            before.inputs,
            before.outputs,
            before.impl_path,
            before.udf_type,
        )
        yield after


class LogicalCreateIndexToFaiss(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALCREATEINDEX)
        super().__init__(RuleType.LOGICAL_CREATE_INDEX_TO_FAISS, pattern)

    def promise(self):
        return Promise.LOGICAL_CREATE_INDEX_TO_FAISS

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalCreateIndex, context: OptimizerContext):
        after = CreateIndexPlan(
            before.name,
            before.table_ref,
            before.col_list,
            before.index_type,
            before.udf_func,
        )
        yield after


class LogicalDropUDFToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALDROPUDF)
        super().__init__(RuleType.LOGICAL_DROP_UDF_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_DROP_UDF_TO_PHYSICAL

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalDropUDF, context: OptimizerContext):
        after = DropUDFPlan(before.name, before.if_exists)
        yield after


class LogicalInsertToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALINSERT)
        super().__init__(RuleType.LOGICAL_INSERT_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_INSERT_TO_PHYSICAL

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalInsert, context: OptimizerContext):
        after = InsertPlan(before.table, before.column_list, before.value_list)
        yield after


class LogicalLoadToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALLOADDATA)
        super().__init__(RuleType.LOGICAL_LOAD_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_LOAD_TO_PHYSICAL

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalLoadData, context: OptimizerContext):
        # Configure the batch_mem_size.
        # We assume the optimizer decides the batch_mem_size.
        # ToDO: Experiment heuristics.

        batch_mem_size = 30000000  # 30mb
        config_batch_mem_size = ConfigurationManager().get_value(
            "executor", "batch_mem_size"
        )
        if config_batch_mem_size:
            batch_mem_size = config_batch_mem_size
        after = LoadDataPlan(
            before.table_info,
            before.path,
            batch_mem_size,
            before.column_list,
            before.file_options,
        )
        yield after


class LogicalUploadToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALUPLOAD)
        super().__init__(RuleType.LOGICAL_UPLOAD_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_UPLOAD_TO_PHYSICAL

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalUpload, context: OptimizerContext):
        # Configure the batch_mem_size.
        # We assume the optimizer decides the batch_mem_size.
        # ToDO: Experiment heuristics.

        batch_mem_size = 30000000  # 30mb
        config_batch_mem_size = ConfigurationManager().get_value(
            "executor", "batch_mem_size"
        )
        if config_batch_mem_size:
            batch_mem_size = config_batch_mem_size
        after = UploadPlan(
            before.path,
            before.video_blob,
            before.table_info,
            batch_mem_size,
            before.column_list,
            before.file_options,
        )

        yield after


class LogicalGetToSeqScan(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALGET)
        super().__init__(RuleType.LOGICAL_GET_TO_SEQSCAN, pattern)

    def promise(self):
        return Promise.LOGICAL_GET_TO_SEQSCAN

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalGet, context: OptimizerContext):
        # Configure the batch_mem_size. It decides the number of rows
        # read in a batch from storage engine.
        # ToDO: Experiment heuristics.

        batch_mem_size = 30000000  # 30mb
        config_batch_mem_size = ConfigurationManager().get_value(
            "executor", "batch_mem_size"
        )
        if config_batch_mem_size:
            batch_mem_size = config_batch_mem_size
        after = SeqScanPlan(None, before.target_list, before.alias)
        after.append_child(
            StoragePlan(
                before.table_obj,
                batch_mem_size=batch_mem_size,
                predicate=before.predicate,
                sampling_rate=before.sampling_rate,
            )
        )
        yield after


class LogicalSampleToUniformSample(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALSAMPLE)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_SAMPLE_TO_UNIFORMSAMPLE, pattern)

    def promise(self):
        return Promise.LOGICAL_SAMPLE_TO_UNIFORMSAMPLE

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalSample, context: OptimizerContext):
        after = SamplePlan(before.sample_freq)
        for child in before.children:
            after.append_child(child)
        yield after


class LogicalDerivedGetToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALQUERYDERIVEDGET)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_DERIVED_GET_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_DERIVED_GET_TO_PHYSICAL

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalQueryDerivedGet, context: OptimizerContext):
        after = SeqScanPlan(before.predicate, before.target_list, before.alias)
        after.append_child(before.children[0])
        yield after


class LogicalUnionToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALUNION)
        # add 2 dummy children
        pattern.append_child(Pattern(OperatorType.DUMMY))
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_UNION_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_UNION_TO_PHYSICAL

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalUnion, context: OptimizerContext):
        after = UnionPlan(before.all)
        for child in before.children:
            after.append_child(child)
        yield after


class LogicalGroupByToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALGROUPBY)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_GROUPBY_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_GROUPBY_TO_PHYSICAL

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalGroupBy, context: OptimizerContext):
        after = GroupByPlan(before.groupby_clause)
        for child in before.children:
            after.append_child(child)
        yield after


class LogicalOrderByToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALORDERBY)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_ORDERBY_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_ORDERBY_TO_PHYSICAL

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalOrderBy, context: OptimizerContext):
        after = OrderByPlan(before.orderby_list)
        for child in before.children:
            after.append_child(child)
        yield after


class LogicalLimitToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALLIMIT)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_LIMIT_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_LIMIT_TO_PHYSICAL

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalLimit, context: OptimizerContext):
        after = LimitPlan(before.limit_count)
        for child in before.children:
            after.append_child(child)
        yield after


class LogicalFunctionScanToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALFUNCTIONSCAN)
        super().__init__(RuleType.LOGICAL_FUNCTION_SCAN_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_FUNCTION_SCAN_TO_PHYSICAL

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalFunctionScan, context: OptimizerContext):
        after = FunctionScanPlan(before.func_expr, before.do_unnest)
        yield after


class LogicalLateralJoinToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALJOIN)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_LATERAL_JOIN_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_LATERAL_JOIN_TO_PHYSICAL

    def check(self, before: Operator, context: OptimizerContext):
        if before.join_type == JoinType.LATERAL_JOIN:
            return True
        else:
            return False

    def apply(self, join_node: LogicalJoin, context: OptimizerContext):
        lateral_join_plan = LateralJoinPlan(join_node.join_predicate)
        lateral_join_plan.join_project = join_node.join_project
        lateral_join_plan.append_child(join_node.lhs())
        lateral_join_plan.append_child(join_node.rhs())
        yield lateral_join_plan


class LogicalJoinToPhysicalHashJoin(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALJOIN)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_JOIN_TO_PHYSICAL_HASH_JOIN, pattern)

    def promise(self):
        return Promise.LOGICAL_JOIN_TO_PHYSICAL_HASH_JOIN

    def check(self, before: Operator, context: OptimizerContext):
        return before.join_type == JoinType.INNER_JOIN

    def apply(self, join_node: LogicalJoin, context: OptimizerContext):
        #          HashJoinPlan                       HashJoinProbePlan
        #          /           \     ->                  /               \
        #         A             B        HashJoinBuildPlan               B
        #                                              /
        #                                            A

        a: Dummy = join_node.lhs()
        b: Dummy = join_node.rhs()
        a_table_aliases = context.memo.get_group_by_id(a.group_id).aliases
        b_table_aliases = context.memo.get_group_by_id(b.group_id).aliases
        join_predicates = join_node.join_predicate
        a_join_keys, b_join_keys = extract_equi_join_keys(
            join_predicates, a_table_aliases, b_table_aliases
        )

        build_plan = HashJoinBuildPlan(join_node.join_type, a_join_keys)
        build_plan.append_child(a)
        probe_side = HashJoinProbePlan(
            join_node.join_type,
            b_join_keys,
            join_predicates,
            join_node.join_project,
        )
        probe_side.append_child(build_plan)
        probe_side.append_child(b)
        yield probe_side


class LogicalCreateMaterializedViewToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICAL_CREATE_MATERIALIZED_VIEW)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_MATERIALIZED_VIEW_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_MATERIALIZED_VIEW_TO_PHYSICAL

    def check(self, grp_id: int, context: OptimizerContext):
        return True

    def apply(self, before: LogicalCreateMaterializedView, context: OptimizerContext):
        after = CreateMaterializedViewPlan(
            before.view,
            columns=before.col_list,
            if_not_exists=before.if_not_exists,
        )
        for child in before.children:
            after.append_child(child)
        yield after


class LogicalFilterToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALFILTER)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_FILTER_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_FILTER_TO_PHYSICAL

    def check(self, grp_id: int, context: OptimizerContext):
        return True

    def apply(self, before: LogicalFilter, context: OptimizerContext):
        after = PredicatePlan(before.predicate)
        for child in before.children:
            after.append_child(child)
        yield after


class LogicalProjectToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALPROJECT)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_PROJECT_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_PROJECT_TO_PHYSICAL

    def check(self, grp_id: int, context: OptimizerContext):
        return True

    def apply(self, before: LogicalProject, context: OptimizerContext):
        after = ProjectPlan(before.target_list)
        for child in before.children:
            after.append_child(child)
        yield after


class LogicalShowToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICAL_SHOW)
        super().__init__(RuleType.LOGICAL_SHOW_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_SHOW_TO_PHYSICAL

    def check(self, grp_id: int, context: OptimizerContext):
        return True

    def apply(self, before: LogicalShow, context: OptimizerContext):
        after = ShowInfoPlan(before.show_type)
        yield after


class LogicalExplainToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALEXPLAIN)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_EXPLAIN_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_EXPLAIN_TO_PHYSICAL

    def check(self, grp_id: int, context: OptimizerContext):
        return True

    def apply(self, before: LogicalExplain, context: OptimizerContext):
        after = ExplainPlan(before.explainable_opr)
        for child in before.children:
            after.append_child(child)
        yield after


class LogicalApplyAndMergeToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICAL_APPLY_AND_MERGE)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_APPLY_AND_MERGE_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_APPLY_AND_MERGE_TO_PHYSICAL

    def check(self, grp_id: int, context: OptimizerContext):
        return True

    def apply(self, before: LogicalApplyAndMerge, context: OptimizerContext):
        after = ApplyAndMergePlan(before.func_expr, before.alias, before.do_unnest)
        for child in before.children:
            after.append_child(child)
        yield after


class LogicalFaissIndexScanToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALFAISSINDEXSCAN)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_FAISS_INDEX_SCAN_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_FAISS_INDEX_SCAN_TO_PHYSICAL

    def check(self, grp_id: int, context: OptimizerContext):
        return True

    def apply(self, before: LogicalFaissIndexScan, context: OptimizerContext):
        after = FaissIndexScanPlan(
            before.index_name, before.limit_count, before.search_query_expr
        )
        for child in before.children:
            after.append_child(child)
        yield after


# IMPLEMENTATION RULES END
##############################################
