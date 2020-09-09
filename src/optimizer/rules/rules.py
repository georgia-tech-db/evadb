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


class RuleType(IntFlag):
    """
    Manages enums for all the supported rules
    """
    # REWRITE RULES(LOGICAL -> LOGICAL)
    EMBED_FILTER_INTO_GET = auto()
    UDF_LTOR = auto()

    REWRITE_DELIMETER = auto()


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
        if (grp_expr.opr.type != pattern.opr_type or
                (len(grp_expr.children) != len(pattern.children))):
            return False
        # recursively compare pattern and input_expr
        for child_id, pattern_child in zip(grp_expr.children,
                                             pattern.children):
            is_equal &= cls._compare_expr_with_pattern(
                child_id, context, pattern_child)
        return is_equal

    @abstractmethod
    def check(self, grp_id: int, context: 'OptimizerContext') -> bool:
        """Check whether the rule is applicable for the input_expr

        Args:
            input_expr ([type]): the before expression

        Returns:
            bool: If the rule is applicable, return true, else false
        """
        raise NotImplementedError

    @abstractmethod
    def apply(self, before) -> Operator:
        """Transform the before expression to the after expression

        Args:
            before ([type]): the before expression

        Returns:
            Operator: the transformed expression
        """
        raise NotImplementedError

##############################################
# RULES START


class EmbedFilterIntoGet(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALFILTER)
        pattern.append_child(Pattern(OperatorType.LOGICALGET))
        super().__init__(RuleType.EMBED_FILTER_INTO_GET, pattern)

    def check(self, grp_id: int, context: 'OptimizerContext'):
        # nothing else to check if logical match found return true
        return Rule._compare_expr_with_pattern(grp_id, context, self._pattern)

    def apply(self, grp_id: int, context: OptimizerContext):
        before = context.memo.get_group(grp_id).get_logical_expr()
        predicate = before.opr.predicate
        
        after = copy.deepcopy(context.memo.get_group(before.children[0]).get_logical_expr())
        after.opr.predicate = predicate
        context.memo.replace_group_expr(grp_id, after)

# RULES END
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
        self._rewrite_rules = [EmbedFilterIntoGet()]

    @property
    def rewrite_rules(self):
        return self._rewrite_rules
