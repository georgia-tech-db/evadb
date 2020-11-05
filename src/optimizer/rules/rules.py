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

from abc import ABC, abstractmethod
from enum import IntFlag, auto
import copy

from src.optimizer.rules.pattern import Pattern
from src.optimizer.operators import OperatorType, Operator
from src.optimizer.optimizer_context import OptimizerContext
from src.optimizer.operators import (
    LogicalCreate, LogicalCreateUDF, LogicalInsert, LogicalLoadData,
    LogicalCreateUDF, LogicalProject, LogicalGet, LogicalFilter,
    LogicalUnion, LogicalCreateMaterializedView, LogicalQueryDerivedGet)
from src.planner.create_plan import CreatePlan
from src.planner.create_udf_plan import CreateUDFPlan
from src.planner.insert_plan import InsertPlan
from src.planner.load_data_plan import LoadDataPlan
from src.planner.seq_scan_plan import SeqScanPlan
from src.planner.storage_plan import StoragePlan
from src.planner.union_plan import UnionPlan
from src.planner.create_mat_view_plan import CreateMaterializedViewPlan
from src.expression.abstract_expression import (
    AbstractExpression, ExpressionType)
from src.expression.function_expression import FunctionExpression
from src.catalog.catalog_manager import CatalogManager
from src.utils.logging_manager import LoggingManager, LoggingLevel
from src.utils.generic_utils import path_to_class


class RuleType(IntFlag):
    """
    Manages enums for all the supported rules
    """
    # REWRITE RULES(LOGICAL -> LOGICAL)
    EMBED_FILTER_INTO_GET = auto()
    EMBED_PROJECT_INTO_GET = auto()
    EMBED_FILTER_INTO_DERIVED_GET = auto()
    EMBED_PROJECT_INTO_DERIVED_GET = auto()
    UDF_LTOR = auto()

    REWRITE_DELIMETER = auto()

    # IMPLEMENTATION RULES (LOGICAL -> PHYSICAL)
    LOGICAL_UNION_TO_PHYSICAL = auto()
    LOGICAL_INSERT_TO_PHYSICAL = auto()
    LOGICAL_LOAD_TO_PHYSICAL = auto()
    LOGICAL_CREATE_TO_PHYSICAL = auto()
    LOGICAL_CREATE_UDF_TO_PHYSICAL = auto()
    LOGICAL_MATERIALIZED_VIEW_TO_PHYSICAL = auto()
    # LOGICAL_PROJECT_TO_PHYSICAL = auto()
    LOGICAL_GET_TO_SEQSCAN = auto()
    LOGICAL_DERIVED_GET_TO_PHYSICAL = auto()
    LOGICAL_UDF_FILTER_TO_PHYSICAL = auto()
    IMPLEMENTATION_DELIMETER = auto()


class Promise(IntFlag):
    """
    Manages order in which rules should be applied.
    Rule with a higher enum will be prefered in case of
    conflict
    """
    # IMPLEMENTATION RULES
    LOGICAL_UNION_TO_PHYSICAL = auto()
    LOGICAL_MATERIALIZED_VIEW_TO_PHYSICAL = auto()
    LOGICAL_INSERT_TO_PHYSICAL = auto()
    LOGICAL_LOAD_TO_PHYSICAL = auto()
    LOGICAL_CREATE_TO_PHYSICAL = auto()
    LOGICAL_CREATE_UDF_TO_PHYSICAL = auto()
    LOGICAL_PROJECT_TO_PHYSICAL = auto()
    LOGICAL_GET_TO_SEQSCAN = auto()
    LOGICAL_DERIVED_GET_TO_PHYSICAL = auto()
    LOGICAL_UDF_FILTER_TO_PHYSICAL = auto()

    # REWRITE RULES
    EMBED_FILTER_INTO_GET = auto()
    EMBED_PROJECT_INTO_GET = auto()
    EMBED_FILTER_INTO_DERIVED_GET = auto()
    EMBED_PROJECT_INTO_DERIVED_GET = auto()
    UDF_LTOR = auto()


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
    def _compare_expr_with_pattern(cls, grp_id, context: OptimizerContext, pattern) -> bool:
        """check if the logical tree of the expression matches the
            provided pattern
        Args:
            input_expr ([type]): expr to match
            pattern: pattern to match with
        Returns:
            bool: If rule pattern matches, return true, else false
        """
        is_equal = True
        grp = context.memo.get_group(grp_id)
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
    def check(self, before: Operator, context: 'OptimizerContext') -> bool:
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

    def check(self, grp_id: int, context: 'OptimizerContext'):
        # nothing else to check if logical match found return true
        return True

    def apply(self, before: LogicalFilter, context: OptimizerContext):
        predicate = before.predicate
        #logical_get = copy.deepcopy(before.children[0])
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

    def check(self, grp_id: int, context: 'OptimizerContext'):
        # nothing else to check if logical match found return true
        return True

    def apply(self, before: LogicalProject, context: OptimizerContext):
        select_list = before.target_list
        #logical_get = copy.deepcopy(before.children[0])
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

    def check(self, grp_id: int, context: 'OptimizerContext'):
        # nothing else to check if logical match found return true
        return True

    def apply(self, before: LogicalFilter, context: OptimizerContext):
        predicate = before.predicate
        #logical_derived_get = copy.deepcopy(before.children[0])
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

    def check(self, grp_id: int, context: 'OptimizerContext'):
        # nothing else to check if logical match found return true
        return True

    def apply(self, before: LogicalProject, context: OptimizerContext):
        select_list = before.target_list
        #logical_derived_get = copy.deepcopy(before.children[0])
        logical_derived_get = before.children[0]
        logical_derived_get.target_list = select_list
        return logical_derived_get

class UdfLTOR(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALFILTER)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.UDF_LTOR, pattern)

    def promise(self):
        return Promise.UDF_LTOR

    def check(self, grp_id: int, context: 'OptimizerContext'):
        # nothing else to check if logical match found return true
        return True

    def _rotate(self, before):
        """Reorders the children based o their estimated execution cost
        After rotation rightmost child has the highest cost

        Args:
            before (AbstractExpression): expression tree to rotate

        Returns:
            int: extimated cost of execution
        """
        children_cost = []
        node_cost = 0
        # fetch cost from the catalog
        if before.etype is ExpressionType.FUNCTION_EXPRESSION:
            node_cost = 1
        for child in before.children:
            cost = self._rotate(child)
            children_cost.append((cost, child))
            node_cost += cost
        children_cost = sorted(children_cost, key=lambda entry: entry[0])
        updated_children = [entry[1] for entry in children_cost]
        before.chidren = updated_children
        return node_cost

    def apply(self, before: LogicalFilter, context: OptimizerContext):
        self._rotate(before.predicate)
        return before


class LogicalUdfFilterToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALFILTER)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_UDF_FILTER_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_UDF_FILTER_TO_PHYSICAL

    def check(self, grp_id: int, context: OptimizerContext):
        return True

    def _bind_udf(self, expr: FunctionExpression):
        """search for all the physical equivalence of this udf
        and replace with the optimal one"""
        if not expr.is_logical():
            return
        catalog = CatalogManager()
        udfs = catalog.get_udfs_by_type(expr.name)
        # randomly selecting right now
        # select the optimal udf
        if udfs:
            udf_obj = udfs[0]
            if expr.output:
                expr.output_obj = catalog.get_udf_io_by_name(expr.output)
                if expr.output_obj is None:
                    LoggingManager().log(
                        'Invalid output {} selected for UDF {}'.format(
                            expr.output, expr.name), LoggingLevel().ERROR)
            expr.function = path_to_class(
                udf_obj.impl_file_path, udf_obj.name)()

        else:
            LoggingManager().log('Invalid UDF{}'.format(expr.name),
                                 LoggingLevel().ERROR)

    def _convert_logical_udfs_to_physical(self, predicate: AbstractExpression):
        if predicate.etype == ExpressionType.FUNCTION_EXPRESSION:
            self._bind_udf(predicate)

        for child in predicate.children:
            self._convert_logical_udfs_to_physical(child)

    def apply(self, before: LogicalGet, context: OptimizerContext):
        self._convert_logical_udfs_to_physical(
            before.predicate)
        return before

# REWRITE RULES END
##############################################


##############################################
# IMPLEMENTATION RULES START
    # LOGICALQUERYDERIVEDGET = auto()


class LogicalCreateToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALCREATE)
        # pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_CREATE_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_CREATE_TO_PHYSICAL

    def check(self, grp_id: int, context: OptimizerContext):
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

    def check(self, grp_id: int, context: OptimizerContext):
        return True

    def apply(self, before: LogicalCreateUDF, context: OptimizerContext):
        after = CreateUDFPlan(before.name, before.if_not_exists, before.inputs,
                              before.outputs, before.impl_path, before.udf_type)
        return after


class LogicalInsertToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALINSERT)
        # pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_INSERT_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_INSERT_TO_PHYSICAL

    def check(self, grp_id: int, context: OptimizerContext):
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

    def check(self, grp_id: int, context: OptimizerContext):
        return True

    def apply(self, before: LogicalLoadData, context: OptimizerContext):
        after = LoadDataPlan(before.table_metainfo, before.path)
        return after


class LogicalGetToSeqScan(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALGET)
        # pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_GET_TO_SEQSCAN, pattern)

    def promise(self):
        return Promise.LOGICAL_GET_TO_SEQSCAN

    def check(self, grp_id: int, context: OptimizerContext):
        return True

    def apply(self, before: LogicalGet, context: OptimizerContext):
        after = SeqScanPlan(before.predicate, before.target_list)
        after.append_child(StoragePlan(before.dataset_metadata))
        return after

class LogicalDerivedGetToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALQUERYDERIVEDGET)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_DERIVED_GET_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_DERIVED_GET_TO_PHYSICAL

    def check(self, grp_id: int, context: OptimizerContext):
        return True

    def apply(self, before: LogicalQueryDerivedGet, context: OptimizerContext):
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

    def check(self, grp_id: int, context: OptimizerContext):
        return True

    def apply(self, before: LogicalUnion, context: OptimizerContext):
        after = UnionPlan(before.all)
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
        after = CreateMaterializedViewPlan(
            before.view, before.col_list, before.if_not_exists)
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
        self._rewrite_rules = [EmbedFilterIntoGet(),
                               EmbedProjectIntoGet(),
                               EmbedFilterIntoDerivedGet(),
                               EmbedProjectIntoDerivedGet()]
                               #    UdfLTOR()]
        self._implementation_rules = [LogicalCreateToPhysical(),
                                      LogicalCreateUDFToPhysical(),
                                      LogicalInsertToPhysical(),
                                      LogicalLoadToPhysical(),
                                      LogicalGetToSeqScan(),
                                      LogicalDerivedGetToPhysical(),
                                      LogicalUnionToPhysical(),
                                      LogicalCreateMaterializedViewToPhysical(),
                                      LogicalUdfFilterToPhysical()
                                      ]

    @property
    def rewrite_rules(self):
        return self._rewrite_rules

    @property
    def implementation_rules(self):
        return self._implementation_rules
