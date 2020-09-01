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
from src.optimizer.rules.patterns import Pattern
from src.optimizer.operators import OperatorType, Operator


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
        _pattern = None
        _rule_type = None

    @property
    def rule_type(self):
        return self._rule_type

    @property
    def pattern(self):
        return self._pattern

    @pattern.setter
    def pattern(self, pattern):
        self._pattern = pattern

    def _compare_expr_with_pattern(self, input_expr) -> bool:
        """check if the logical tree of the expression matches the

        Args:
            input_expr ([type]): expr to compare

        Returns:
            bool: If rule pattern matches, return true, else false
        """
        is_equal = False
        if input_expr is None or not isinstance(input_expr, Operator):
            return is_equal
        if (input_expr.type != self.pattern.opr_type or
                (len(input_expr.children) != len(self.pattern.children))):
            return is_equal
        # recursively compare pattern and input_expr
        for expr_child, pattern_child in zip(input_expr.children,
                                             self.pattern.children):
            is_equal |= self._compare_expr_with_pattern(
                expr_child, pattern_child)
        return is_equal

    @abstractmethod
    def check(self, input_expr) -> bool:
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

    def check(self, input_expr):
        # nothing else to check if logical match found return true
        return super()._compare_expr_with_pattern(input_expr)

    def apply(self, before):
        logical_get = before.children[0]
        filter_predicate = before.predicate
        logical_get.predicate = filter_predicate
        return logical_get

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
