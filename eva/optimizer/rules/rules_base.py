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

from abc import ABC, abstractmethod
from enum import Flag, IntEnum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eva.optimizer.optimizer_context import OptimizerContext

from eva.optimizer.operators import Operator


class RuleType(Flag):
    """
    Manages enums for all the supported rules
    """

    # Don't move this enum, else will break rule exploration logic
    INVALID_RULE = 0

    # REWRITE RULES(LOGICAL -> LOGICAL)
    EMBED_FILTER_INTO_GET = auto()
    EMBED_FILTER_INTO_DERIVED_GET = auto()
    EMBED_SAMPLE_INTO_GET = auto()
    EMBED_PROJECT_INTO_DERIVED_GET = auto()
    EMBED_PROJECT_INTO_GET = auto()
    PUSHDOWN_FILTER_THROUGH_JOIN = auto()
    REWRITE_DELIMETER = auto()

    # TRANSFORMATION RULES (LOGICAL -> LOGICAL)
    LOGICAL_INNER_JOIN_COMMUTATIVITY = auto()
    TRANSFORMATION_DELIMETER = auto()

    # IMPLEMENTATION RULES (LOGICAL -> PHYSICAL)
    LOGICAL_EXCHANGE_TO_PHYSICAL = auto()
    LOGICAL_UNION_TO_PHYSICAL = auto()
    LOGICAL_GROUPBY_TO_PHYSICAL = auto()
    LOGICAL_ORDERBY_TO_PHYSICAL = auto()
    LOGICAL_LIMIT_TO_PHYSICAL = auto()
    LOGICAL_INSERT_TO_PHYSICAL = auto()
    LOGICAL_LOAD_TO_PHYSICAL = auto()
    LOGICAL_UPLOAD_TO_PHYSICAL = auto()
    LOGICAL_CREATE_TO_PHYSICAL = auto()
    LOGICAL_RENAME_TO_PHYSICAL = auto()
    LOGICAL_DROP_TO_PHYSICAL = auto()
    LOGICAL_CREATE_UDF_TO_PHYSICAL = auto()
    LOGICAL_MATERIALIZED_VIEW_TO_PHYSICAL = auto()
    LOGICAL_GET_TO_SEQSCAN = auto()
    LOGICAL_SAMPLE_TO_UNIFORMSAMPLE = auto()
    LOGICAL_DERIVED_GET_TO_PHYSICAL = auto()
    LOGICAL_LATERAL_JOIN_TO_PHYSICAL = auto()
    LOGICAL_JOIN_TO_PHYSICAL_HASH_JOIN = auto()
    LOGICAL_FUNCTION_SCAN_TO_PHYSICAL = auto()
    LOGICAL_FILTER_TO_PHYSICAL = auto()
    LOGICAL_PROJECT_TO_PHYSICAL = auto()
    LOGICAL_SHOW_TO_PHYSICAL = auto()
    LOGICAL_DROP_UDF_TO_PHYSICAL = auto()
    LOGICAL_EXPLAIN_TO_PHYSICAL = auto()
    IMPLEMENTATION_DELIMETER = auto()

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
    LOGICAL_MATERIALIZED_VIEW_TO_PHYSICAL = auto()
    LOGICAL_GROUPBY_TO_PHYSICAL = auto()
    LOGICAL_ORDERBY_TO_PHYSICAL = auto()
    LOGICAL_LIMIT_TO_PHYSICAL = auto()
    LOGICAL_INSERT_TO_PHYSICAL = auto()
    LOGICAL_RENAME_TO_PHYSICAL = auto()
    LOGICAL_DROP_TO_PHYSICAL = auto()
    LOGICAL_LOAD_TO_PHYSICAL = auto()
    LOGICAL_UPLOAD_TO_PHYSICAL = auto()
    LOGICAL_CREATE_TO_PHYSICAL = auto()
    LOGICAL_CREATE_UDF_TO_PHYSICAL = auto()
    LOGICAL_SAMPLE_TO_UNIFORMSAMPLE = auto()
    LOGICAL_GET_TO_SEQSCAN = auto()
    LOGICAL_DERIVED_GET_TO_PHYSICAL = auto()
    LOGICAL_LATERAL_JOIN_TO_PHYSICAL = auto()
    LOGICAL_JOIN_TO_PHYSICAL_HASH_JOIN = auto()
    LOGICAL_FUNCTION_SCAN_TO_PHYSICAL = auto()
    LOGICAL_FILTER_TO_PHYSICAL = auto()
    LOGICAL_PROJECT_TO_PHYSICAL = auto()
    LOGICAL_SHOW_TO_PHYSICAL = auto()
    LOGICAL_DROP_UDF_TO_PHYSICAL = auto()
    LOGICAL_EXPLAIN_TO_PHYSICAL = auto()
    IMPLEMENTATION_DELIMETER = auto()

    # TRANSFORMATION RULES (LOGICAL -> LOGICAL)
    LOGICAL_INNER_JOIN_COMMUTATIVITY = auto()

    # REWRITE RULES
    EMBED_FILTER_INTO_GET = auto()
    EMBED_PROJECT_INTO_GET = auto()
    EMBED_FILTER_INTO_DERIVED_GET = auto()
    EMBED_PROJECT_INTO_DERIVED_GET = auto()
    EMBED_SAMPLE_INTO_GET = auto()
    PUSHDOWN_FILTER_THROUGH_JOIN = auto()


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
