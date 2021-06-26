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
    from src.optimizer.optimizer_context import OptimizerContext

from src.optimizer.rules.pattern import Pattern
from src.optimizer.operators import OperatorType, Operator
from src.optimizer.operators import (
    LogicalCreate, LogicalInsert, LogicalLoadData, LogicalUpload,
    LogicalCreateUDF, LogicalProject, LogicalGet, LogicalFilter,
    LogicalUnion, LogicalOrderBy, LogicalLimit, LogicalQueryDerivedGet,
    LogicalSample)
from src.planner.create_plan import CreatePlan
from src.planner.create_udf_plan import CreateUDFPlan
from src.planner.insert_plan import InsertPlan
from src.planner.load_data_plan import LoadDataPlan
from src.planner.upload_plan import UploadPlan
from src.planner.seq_scan_plan import SeqScanPlan
from src.planner.storage_plan import StoragePlan
from src.planner.union_plan import UnionPlan
from src.planner.orderby_plan import OrderByPlan
from src.planner.limit_plan import LimitPlan
from src.planner.sample_plan import SamplePlan


class RuleType(Flag):
    """
    Manages enums for all the supported rules
    """
    # Don't move this enum, else will break rule exploration logic
    INVALID_RULE = 0

    # REWRITE RULES(LOGICAL -> LOGICAL)
    EMBED_FILTER_INTO_GET = auto()
    EMBED_PROJECT_INTO_GET = auto()
    EMBED_FILTER_INTO_DERIVED_GET = auto()
    EMBED_PROJECT_INTO_DERIVED_GET = auto()
    PUSHDOWN_FILTER_THROUGH_SAMPLE = auto()
    PUSHDOWN_PROJECT_THROUGH_SAMPLE = auto()

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
    LOGICAL_GET_TO_SEQSCAN = auto()
    LOGICAL_SAMPLE_TO_UNIFORMSAMPLE = auto()
    LOGICAL_DERIVED_GET_TO_PHYSICAL = auto()
    IMPLEMENTATION_DELIMETER = auto()


class Promise(IntEnum):
    """
    Manages order in which rules should be applied.
    Rule with a higher enum will be prefered in case of
    conflict
    """
    # IMPLEMENTATION RULES
    LOGICAL_UNION_TO_PHYSICAL = auto()
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
            logical->phyical
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

    @classmethod
    def _compare_expr_with_pattern(cls,
                                   grp_id,
                                   context: OptimizerContext,
                                   pattern) -> bool:
        """check if the logical tree of the expression matches the
            provided pattern
        Args:
            input_expr ([type]): expr to match
            pattern: pattern to match with
        Returns:
            bool: If rule pattern matches, return true, else false
        """
        is_equal = True
        grp = context.memo.groups[grp_id]
        grp_expr = grp.get_logical_expr()
        if grp_expr is None:
            return False
        if (grp_expr.opr.opr_type != pattern.opr_type or
                (len(grp_expr.children) != len(pattern.children))):
            return False
        # recursively compare pattern and input_expr
        for child_id, pattern_child in zip(grp_expr.children,
                                           pattern.children):
            is_equal &= cls._compare_expr_with_pattern(
                child_id, context, pattern_child)
        return is_equal

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
        # logical_get = copy.deepcopy(before.children[0])
        logical_get = before.children[0]
        logical_get.predicate = predicate
        return logical_get


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
        # logical_get = copy.deepcopy(before.children[0])
        logical_get = before.children[0]
        logical_get.target_list = select_list
        return logical_get

# For nestes queries


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
        # logical_derived_get = copy.deepcopy(before.children[0])
        logical_derived_get = before.children[0]
        logical_derived_get.predicate = predicate
        return logical_derived_get


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
        select_list = before.target_list
        # logical_derived_get = copy.deepcopy(before.children[0])
        logical_derived_get = before.children[0]
        logical_derived_get.target_list = select_list
        return logical_derived_get


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
        logical_get.predicate = before.predicate
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
        logical_get.target_list = before.target_list
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
        after = InsertPlan(before.video_catalog_id,
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
        after = LoadDataPlan(before.table_metainfo, before.path)
        return after


class LogicalUploadToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALUPLOAD)
        # pattern.append_child(Pattern(OperatorType.DUMMY))
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
        after = SeqScanPlan(before.predicate, before.target_list)
        after.append_child(StoragePlan(before.dataset_metadata))
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
        self._rewrite_rules = [
            EmbedFilterIntoGet(),
            EmbedProjectIntoGet(),
            EmbedFilterIntoDerivedGet(),
            EmbedProjectIntoDerivedGet(),
            PushdownFilterThroughSample(),
            PushdownProjectThroughSample()
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
            LogicalLimitToPhysical()
        ]

    @property
    def rewrite_rules(self):
        return self._rewrite_rules

    @property
    def implementation_rules(self):
        return self._implementation_rules
