# coding=utf-8
# Copyright 2018-2023 EvaDB
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
from enum import Flag, IntEnum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from evadb.optimizer.optimizer_context import OptimizerContext

from evadb.optimizer.operators import Operator


class RuleType(Flag):
    """
    Manages enums for all the supported rules
    """

    # Don't move this enum, else will break rule exploration logic
    INVALID_RULE = 0

    # REWRITE RULES TOP DOWN APPLY FIRST (LOGICAL -> LOGICAL)
    XFORM_LATERAL_JOIN_TO_LINEAR_FLOW = auto()
    XFORM_EXTRACT_OBJECT_TO_LINEAR_FLOW = auto()
    TOP_DOWN_DELIMITER = auto()

    # REWRITE RULES BOTTOM UP APPLY SECOND (LOGICAL -> LOGICAL)
    EMBED_FILTER_INTO_GET = auto()
    EMBED_SAMPLE_INTO_GET = auto()
    PUSHDOWN_FILTER_THROUGH_JOIN = auto()
    PUSHDOWN_FILTER_THROUGH_APPLY_AND_MERGE = auto()
    COMBINE_SIMILARITY_ORDERBY_AND_LIMIT_TO_VECTOR_INDEX_SCAN = auto()
    REORDER_PREDICATES = auto()

    REWRITE_DELIMITER = auto()

    # TRANSFORMATION RULES (LOGICAL -> LOGICAL)
    LOGICAL_INNER_JOIN_COMMUTATIVITY = auto()
    CACHE_FUNCTION_EXPRESISON_IN_APPLY = auto()
    CACHE_FUNCTION_EXPRESISON_IN_FILTER = auto()
    CACHE_FUNCTION_EXPRESISON_IN_PROJECT = auto()
    TRANSFORMATION_DELIMITER = auto()  # do not reposition

    # IMPLEMENTATION RULES (LOGICAL -> PHYSICAL)
    LOGICAL_EXCHANGE_TO_PHYSICAL = auto()
    LOGICAL_UNION_TO_PHYSICAL = auto()
    LOGICAL_GROUPBY_TO_PHYSICAL = auto()
    LOGICAL_ORDERBY_TO_PHYSICAL = auto()
    LOGICAL_LIMIT_TO_PHYSICAL = auto()
    LOGICAL_INSERT_TO_PHYSICAL = auto()
    LOGICAL_DELETE_TO_PHYSICAL = auto()
    LOGICAL_LOAD_TO_PHYSICAL = auto()
    LOGICAL_CREATE_TO_PHYSICAL = auto()
    LOGICAL_CREATE_FROM_SELECT_TO_PHYSICAL = auto()
    LOGICAL_RENAME_TO_PHYSICAL = auto()
    LOGICAL_DROP_OBJECT_TO_PHYSICAL = auto()
    LOGICAL_CREATE_UDF_TO_PHYSICAL = auto()
    LOGICAL_CREATE_UDF_FROM_SELECT_TO_PHYSICAL = auto()
    LOGICAL_GET_TO_SEQSCAN = auto()
    LOGICAL_SAMPLE_TO_UNIFORMSAMPLE = auto()
    LOGICAL_DERIVED_GET_TO_PHYSICAL = auto()
    LOGICAL_LATERAL_JOIN_TO_PHYSICAL = auto()
    LOGICAL_JOIN_TO_PHYSICAL_HASH_JOIN = auto()
    LOGICAL_JOIN_TO_PHYSICAL_NESTED_LOOP_JOIN = auto()
    LOGICAL_FUNCTION_SCAN_TO_PHYSICAL = auto()
    LOGICAL_FILTER_TO_PHYSICAL = auto()
    LOGICAL_PROJECT_TO_PHYSICAL = auto()
    LOGICAL_SHOW_TO_PHYSICAL = auto()
    LOGICAL_EXPLAIN_TO_PHYSICAL = auto()
    LOGICAL_CREATE_INDEX_TO_VECTOR_INDEX = auto()
    LOGICAL_APPLY_AND_MERGE_TO_PHYSICAL = auto()
    LOGICAL_VECTOR_INDEX_SCAN_TO_PHYSICAL = auto()
    IMPLEMENTATION_DELIMITER = auto()

    NUM_RULES = auto()


class Promise(IntEnum):
    """
    Manages order in which rules should be applied.
    Rule with a higher enum will be preferred in case of
    conflict
    """

    # IMPLEMENTATION RULES
    LOGICAL_EXCHANGE_TO_PHYSICAL = auto()
    LOGICAL_UNION_TO_PHYSICAL = auto()
    LOGICAL_GROUPBY_TO_PHYSICAL = auto()
    LOGICAL_ORDERBY_TO_PHYSICAL = auto()
    LOGICAL_LIMIT_TO_PHYSICAL = auto()
    LOGICAL_INSERT_TO_PHYSICAL = auto()
    LOGICAL_DELETE_TO_PHYSICAL = auto()
    LOGICAL_RENAME_TO_PHYSICAL = auto()
    LOGICAL_DROP_OBJECT_TO_PHYSICAL = auto()
    LOGICAL_LOAD_TO_PHYSICAL = auto()
    LOGICAL_CREATE_TO_PHYSICAL = auto()
    LOGICAL_CREATE_FROM_SELECT_TO_PHYSICAL = auto()
    LOGICAL_CREATE_UDF_TO_PHYSICAL = auto()
    LOGICAL_CREATE_UDF_FROM_SELECT_TO_PHYSICAL = auto()
    LOGICAL_SAMPLE_TO_UNIFORMSAMPLE = auto()
    LOGICAL_GET_TO_SEQSCAN = auto()
    LOGICAL_DERIVED_GET_TO_PHYSICAL = auto()
    LOGICAL_LATERAL_JOIN_TO_PHYSICAL = auto()

    LOGICAL_JOIN_TO_PHYSICAL_HASH_JOIN = auto()
    LOGICAL_JOIN_TO_PHYSICAL_NESTED_LOOP_JOIN = auto()

    LOGICAL_FUNCTION_SCAN_TO_PHYSICAL = auto()
    LOGICAL_FILTER_TO_PHYSICAL = auto()
    LOGICAL_PROJECT_TO_PHYSICAL = auto()
    LOGICAL_SHOW_TO_PHYSICAL = auto()
    LOGICAL_EXPLAIN_TO_PHYSICAL = auto()
    LOGICAL_CREATE_INDEX_TO_VECTOR_INDEX = auto()
    LOGICAL_APPLY_AND_MERGE_TO_PHYSICAL = auto()
    LOGICAL_VECTOR_INDEX_SCAN_TO_PHYSICAL = auto()

    # IMPLEMENTATION DELIMITER
    IMPLEMENTATION_DELIMITER = auto()

    # TRANSFORMATION RULES (LOGICAL -> LOGICAL)
    LOGICAL_INNER_JOIN_COMMUTATIVITY = auto()
    CACHE_FUNCTION_EXPRESISON_IN_APPLY = auto()
    CACHE_FUNCTION_EXPRESISON_IN_FILTER = auto()
    CACHE_FUNCTION_EXPRESISON_IN_PROJECT = auto()

    # REWRITE RULES
    EMBED_FILTER_INTO_GET = auto()
    EMBED_SAMPLE_INTO_GET = auto()
    XFORM_EXTRACT_OBJECT_TO_LINEAR_FLOW = auto()
    XFORM_LATERAL_JOIN_TO_LINEAR_FLOW = auto()
    PUSHDOWN_FILTER_THROUGH_JOIN = auto()
    PUSHDOWN_FILTER_THROUGH_APPLY_AND_MERGE = auto()
    COMBINE_SIMILARITY_ORDERBY_AND_LIMIT_TO_VECTOR_INDEX_SCAN = auto()
    REORDER_PREDICATES = auto()


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

    def top_match(self, opr: Operator) -> bool:
        return opr.opr_type == self.pattern.opr_type

    def is_implementation_rule(self):
        return self.rule_type.value > RuleType.TRANSFORMATION_DELIMITER.value

    def is_logical_rule(self):
        return (
            self.rule_type.value > RuleType.REWRITE_DELIMITER.value
            and self.rule_type.value < RuleType.TRANSFORMATION_DELIMITER.value
        )

    def is_stage_two_rewrite_rules(self):
        return (
            self.rule_type.value > RuleType.TOP_DOWN_DELIMITER.value
            and self.rule_type.value < RuleType.REWRITE_DELIMITER.value
        )

    def is_stage_one_rewrite_rules(self):
        return self.rule_type.value < RuleType.TOP_DOWN_DELIMITER.value

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
