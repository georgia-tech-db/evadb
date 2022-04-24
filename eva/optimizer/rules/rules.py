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

from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Flag, auto, IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eva.optimizer.optimizer_context import OptimizerContext

from eva.optimizer.rules.pattern import Pattern
from eva.optimizer.operators import OperatorType, Operator
from eva.optimizer.operators import (
    LogicalCreate, LogicalInsert, LogicalLoadData, LogicalUpload,
    LogicalCreateUDF, LogicalProject, LogicalGet, LogicalFilter,
    LogicalUnion, LogicalOrderBy, LogicalLimit, LogicalQueryDerivedGet,
    LogicalSample, LogicalCreateMaterializedView)
from eva.planner.create_plan import CreatePlan
from eva.planner.create_udf_plan import CreateUDFPlan
from eva.planner.create_mat_view_plan import CreateMaterializedViewPlan
from eva.planner.insert_plan import InsertPlan
from eva.planner.load_data_plan import LoadDataPlan
from eva.planner.upload_plan import UploadPlan
from eva.planner.seq_scan_plan import SeqScanPlan
from eva.planner.storage_plan import StoragePlan
from eva.planner.union_plan import UnionPlan
from eva.planner.orderby_plan import OrderByPlan
from eva.planner.limit_plan import LimitPlan
from eva.planner.sample_plan import SamplePlan
from eva.configuration.configuration_manager import ConfigurationManager


class RuleType(Flag):
    """
    Manages enums for all the supported rules
    """
    # Don't move this enum, else will break rule exploration logic
    INVALID_RULE = 0

    # REWRITE RULES(LOGICAL -> LOGICAL)
    EMBED_FILTER_INTO_GET = auto()
    EMBED_FILTER_INTO_DERIVED_GET = auto()
    PUSHDOWN_FILTER_THROUGH_SAMPLE = auto()
    PUSHDOWN_PROJECT_THROUGH_SAMPLE = auto()
    EMBED_PROJECT_INTO_DERIVED_GET = auto()
    EMBED_PROJECT_INTO_GET = auto()

    REWRITE_DELIMETER = auto()

    # IMPLEMENTATION RULES (LOGICAL -> PHYSICAL)
    LOGICAL_UNION_TO_PHYSICAL = auto()
    LOGICAL_ORDERBY_TO_PHYSICAL = auto()
    LOGICAL_LIMIT_TO_PHYSICAL = auto()
    LOGICAL_INSERT_TO_PHYSICAL = auto()
    LOGICAL_LOAD_TO_PHYSICAL = auto()
    LOGICAL_UPLOAD_TO_PHYSICAL = auto()
    LOGICAL_CREATE_TO_PHYSICAL = auto()
    LOGICAL_CREATE_UDF_TO_PHYSICAL = auto()
    LOGICAL_MATERIALIZED_VIEW_TO_PHYSICAL = auto()
    LOGICAL_GET_TO_SEQSCAN = auto()
    LOGICAL_SAMPLE_TO_UNIFORMSAMPLE = auto()
    LOGICAL_DERIVED_GET_TO_PHYSICAL = auto()
    IMPLEMENTATION_DELIMETER = auto()

    NUM_RULES = auto()


class Promise(IntEnum):
    """
    Manages order in which rules should be applied.
    Rule with a higher enum will be preferred in case of
    conflict
    """
    # IMPLEMENTATION RULES
    LOGICAL_UNION_TO_PHYSICAL = auto()
    LOGICAL_MATERIALIZED_VIEW_TO_PHYSICAL = auto()
    LOGICAL_ORDERBY_TO_PHYSICAL = auto()
    LOGICAL_LIMIT_TO_PHYSICAL = auto()
    LOGICAL_INSERT_TO_PHYSICAL = auto()
    LOGICAL_LOAD_TO_PHYSICAL = auto()
    LOGICAL_UPLOAD_TO_PHYSICAL = auto()
    LOGICAL_CREATE_TO_PHYSICAL = auto()
    LOGICAL_CREATE_UDF_TO_PHYSICAL = auto()
    LOGICAL_SAMPLE_TO_UNIFORMSAMPLE = auto()
    LOGICAL_GET_TO_SEQSCAN = auto()
    LOGICAL_DERIVED_GET_TO_PHYSICAL = auto()
    IMPLEMENTATION_DELIMETER = auto()

    # REWRITE RULES
    EMBED_FILTER_INTO_GET = auto()
    EMBED_PROJECT_INTO_GET = auto()
    EMBED_FILTER_INTO_DERIVED_GET = auto()
    EMBED_PROJECT_INTO_DERIVED_GET = auto()
    PUSHDOWN_FILTER_THROUGH_SAMPLE = auto()
    PUSHDOWN_PROJECT_THROUGH_SAMPLE = auto()


class Rule(ABC):
    """Base class to define any optimization rule

    Arguments:
        rule_type(RuleType): type of the rule, can be rewrite,
            logical->physical
        pattern: the match pattern for the rule
    """

    def __init__(self, rule_type: RuleType, pattern=None):
        self._pattern = pattern
        self._rule_type = rule_type

    @property
    def rule_type(self):
        return self._rule_type

    @property
    def pattern(self):
        return self._pattern

    @pattern.setter
    def pattern(self, pattern):
        self._pattern = pattern

    def top_match(self, opr: Operator) -> bool:
        return opr.opr_type == self.pattern.opr_type

    @abstractmethod
    def promise(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def check(self, before: Operator, context: OptimizerContext) -> bool:
        """Check whether the rule is applicable for the input_expr

        Args:
            before (Operator): the before operator expression

        Returns:
            bool: If the rule is applicable, return true, else false
        """
        raise NotImplementedError

    @abstractmethod
    def apply(self, before: Operator) -> Operator:
        """Transform the before expression to the after expression

        Args:
            before (Operator): the before expression

        Returns:
            Operator: the transformed expression
        """
        raise NotImplementedError

##############################################
# REWRITE RULES START


class EmbedFilterIntoGet(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALFILTER)
        pattern.append_child(Pattern(OperatorType.LOGICALGET))
        super().__init__(RuleType.EMBED_FILTER_INTO_GET, pattern)

    def promise(self):
        return Promise.EMBED_FILTER_INTO_GET

    def check(self, before: Operator, context: OptimizerContext):
        # nothing else to check if logical match found return true
        return True

    def apply(self, before: LogicalFilter, context: OptimizerContext):
        predicate = before.predicate
        lget = before.children[0]
        new_get_opr = LogicalGet(
            lget.video, lget.dataset_metadata,
            predicate, lget.target_list, lget.children)
        return new_get_opr


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
        select_list = before.target_list
        lget = before.children[0]
        new_get_opr = LogicalGet(
            lget.video, lget.dataset_metadata,
            lget.predicate, select_list, lget.children)
        return new_get_opr

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
            predicate, ld_get.target_list, ld_get.children)
        return new_opr


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
            ld_get.predicate, target_list, ld_get.children)
        return new_opr


class PushdownFilterThroughSample(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALFILTER)
        pattern_sample = Pattern(OperatorType.LOGICALSAMPLE)
        pattern_sample.append_child(Pattern(OperatorType.LOGICALGET))
        pattern.append_child(pattern_sample)
        super().__init__(RuleType.PUSHDOWN_FILTER_THROUGH_SAMPLE, pattern)

    def promise(self):
        return Promise.PUSHDOWN_FILTER_THROUGH_SAMPLE

    def check(self, before: Operator, context: OptimizerContext):
        # nothing else to check if logical match found return true
        return True

    def apply(self, before: LogicalFilter, context: OptimizerContext):
        sample = before.children[0]
        logical_get = sample.children[0]
        new_filter = LogicalFilter(before.predicate)
        new_filter.append_child(logical_get)
        sample.clear_children()
        sample.append_child(new_filter)
        return sample


class PushdownProjectThroughSample(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALPROJECT)
        pattern_sample = Pattern(OperatorType.LOGICALSAMPLE)
        pattern_sample.append_child(Pattern(OperatorType.LOGICALGET))
        pattern.append_child(pattern_sample)
        super().__init__(RuleType.PUSHDOWN_PROJECT_THROUGH_SAMPLE, pattern)

    def promise(self):
        return Promise.PUSHDOWN_PROJECT_THROUGH_SAMPLE

    def check(self, before: Operator, context: OptimizerContext):
        # nothing else to check if logical match found return true
        return True

    def apply(self, before: LogicalProject, context: OptimizerContext):
        sample = before.children[0]
        logical_get = sample.children[0]
        new_project = LogicalProject(before.target_list)
        new_project.append_child(logical_get)
        sample.clear_children()
        sample.append_child(new_project)
        return sample


# REWRITE RULES END
##############################################


##############################################
# IMPLEMENTATION RULES START


class LogicalCreateToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALCREATE)
        # pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_CREATE_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_CREATE_TO_PHYSICAL

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalCreate, context: OptimizerContext):
        after = CreatePlan(before.video, before.column_list,
                           before.if_not_exists)
        return after


class LogicalCreateUDFToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALCREATEUDF)
        # pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_CREATE_UDF_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_CREATE_UDF_TO_PHYSICAL

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalCreateUDF, context: OptimizerContext):
        after = CreateUDFPlan(before.name,
                              before.if_not_exists,
                              before.inputs,
                              before.outputs,
                              before.impl_path,
                              before.udf_type)
        return after


class LogicalInsertToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALINSERT)
        # pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_INSERT_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_INSERT_TO_PHYSICAL

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalInsert, context: OptimizerContext):
        after = InsertPlan(before.table_metainfo,
                           before.column_list, before.value_list)
        return after


class LogicalLoadToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALLOADDATA)
        # pattern.append_child(Pattern(OperatorType.DUMMY))
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
            "executor", "batch_mem_size")
        if config_batch_mem_size:
            batch_mem_size = config_batch_mem_size
        after = LoadDataPlan(before.table_metainfo,
                             before.path,
                             batch_mem_size,
                             before.column_list,
                             before.file_options)
        return after


class LogicalUploadToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALUPLOAD)
        super().__init__(RuleType.LOGICAL_UPLOAD_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_UPLOAD_TO_PHYSICAL

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalUpload, context: OptimizerContext):
        after = UploadPlan(before.path, before.video_blob)
        return after


class LogicalGetToSeqScan(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALGET)
        # pattern.append_child(Pattern(OperatorType.DUMMY))
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
            "executor", "batch_mem_size")
        if config_batch_mem_size:
            batch_mem_size = config_batch_mem_size
        after = SeqScanPlan(before.predicate, before.target_list)
        after.append_child(StoragePlan(
            before.dataset_metadata, batch_mem_size=batch_mem_size))
        return after


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
        return after


class LogicalDerivedGetToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALQUERYDERIVEDGET)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_DERIVED_GET_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_DERIVED_GET_TO_PHYSICAL

    def check(self, before: Operator, context: OptimizerContext):
        return True

    def apply(self, before: LogicalQueryDerivedGet,
              context: OptimizerContext):
        after = SeqScanPlan(before.predicate, before.target_list)
        after.append_child(before.children[0])
        return after


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
        return after


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
        return after


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
        return after


class LogicalCreateMaterializedViewToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICAL_CREATE_MATERIALIZED_VIEW)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_MATERIALIZED_VIEW_TO_PHYSICAL,
                         pattern)

    def promise(self):
        return Promise.LOGICAL_MATERIALIZED_VIEW_TO_PHYSICAL

    def check(self, grp_id: int, context: OptimizerContext):
        return True

    def apply(self, before: LogicalCreateMaterializedView,
              context: OptimizerContext):
        after = CreateMaterializedViewPlan(before.view,
                                           columns=before.col_list,
                                           if_not_exists=before.if_not_exists)
        for child in before.children:
            after.append_child(child)
        return after

# IMPLEMENTATION RULES END
##############################################


class RulesManager:
    """Singelton class to manage all the rules in our system
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RulesManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):

        self._tmp_rewrite_rules = [
            EmbedProjectIntoGet(),
            EmbedProjectIntoDerivedGet(),
            PushdownProjectThroughSample()
        ]

        self._rewrite_rules = [
            EmbedFilterIntoGet(),
            EmbedFilterIntoDerivedGet(),
            PushdownFilterThroughSample()
        ]

        self._implementation_rules = [
            LogicalCreateToPhysical(),
            LogicalCreateUDFToPhysical(),
            LogicalInsertToPhysical(),
            LogicalLoadToPhysical(),
            LogicalUploadToPhysical(),
            LogicalSampleToUniformSample(),
            LogicalGetToSeqScan(),
            LogicalDerivedGetToPhysical(),
            LogicalUnionToPhysical(),
            LogicalOrderByToPhysical(),
            LogicalLimitToPhysical(),
            LogicalCreateMaterializedViewToPhysical()
        ]
        self._all_rules = self._tmp_rewrite_rules + \
            self._rewrite_rules + self._implementation_rules

    @property
    def rewrite_rules(self):
        return self._rewrite_rules

    @property
    def tmp_rewrite_rules(self):
        return self._tmp_rewrite_rules

    @property
    def implementation_rules(self):
        return self._implementation_rules

    @property
    def all_rules(self):
        return self._all_rules
