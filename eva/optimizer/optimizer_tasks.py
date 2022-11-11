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

from enum import IntEnum, auto
from typing import TYPE_CHECKING, List

from eva.optimizer.binder import Binder
from eva.optimizer.group import Group
from eva.optimizer.group_expression import GroupExpression
from eva.optimizer.property import PropertyType
from eva.optimizer.rules.rules_base import Rule
from eva.optimizer.rules.rules_manager import RulesManager
from eva.utils.logging_manager import logger

if TYPE_CHECKING:
    from eva.optimizer.optimizer_context import OptimizerContext


class OptimizerTaskType(IntEnum):
    """Manages Enum for all the supported optimizer tasks"""

    TOP_DOWN_REWRITE = auto()
    BOTTOM_UP_REWRITE = auto()
    OPTIMIZE_EXPRESSION = auto()
    OPTIMIZE_GROUP = auto()
    OPTIMIZE_INPUTS = auto()
    APPLY_RULE = auto()
    EXPLORE_GROUP = auto()


class OptimizerTask:
    def __init__(
        self, optimizer_context: OptimizerContext, task_type: OptimizerTaskType
    ):
        self._task_type = task_type
        self._optimizer_context = optimizer_context

    @property
    def task_type(self):
        return self._task_type

    @property
    def optimizer_context(self):
        return self._optimizer_context

    def execute(self):
        raise NotImplementedError


class TopDownRewrite(OptimizerTask):
    def __init__(
        self,
        root_expr: GroupExpression,
        rule_set: List[Rule],
        optimizer_context: OptimizerContext,
    ):
        self.root_expr = root_expr
        self.rule_set = rule_set
        super().__init__(optimizer_context, OptimizerTaskType.TOP_DOWN_REWRITE)

    def execute(self):
        valid_rules = []
        for rule in self.rule_set:
            if not self.root_expr.is_rule_explored(rule.rule_type) and rule.top_match(
                self.root_expr.opr
            ):
                valid_rules.append(rule)

        # sort the rules by promise
        valid_rules = sorted(valid_rules, key=lambda x: x.promise())
        for rule in valid_rules:
            binder = Binder(self.root_expr, rule.pattern, self.optimizer_context.memo)
            for match in iter(binder):
                if not rule.check(match, self.optimizer_context):
                    continue
                logger.info(
                    "In TopDown, Rule {} matched for {}".format(rule, self.root_expr)
                )
                after = rule.apply(match, self.optimizer_context)
                new_expr = self.optimizer_context.replace_expression(
                    after, self.root_expr.group_id
                )
                self.optimizer_context.task_stack.push(
                    TopDownRewrite(new_expr, self.rule_set, self.optimizer_context)
                )

                self.root_expr.mark_rule_explored(rule.rule_type)
        for child in self.root_expr.children:
            child_expr = self.optimizer_context.memo.groups[child].logical_exprs[0]
            self.optimizer_context.task_stack.push(
                TopDownRewrite(child_expr, self.rule_set, self.optimizer_context)
            )


class BottomUpRewrite(OptimizerTask):
    def __init__(
        self,
        root_expr: GroupExpression,
        rule_set: List[Rule],
        optimizer_context: OptimizerContext,
        children_explored=False,
    ):
        super().__init__(optimizer_context, OptimizerTaskType.BOTTOM_UP_REWRITE)
        self._children_explored = children_explored
        self.root_expr = root_expr
        self.rule_set = rule_set

    def execute(self):
        if not self._children_explored:
            self.optimizer_context.task_stack.push(
                BottomUpRewrite(
                    self.root_expr, self.rule_set, self.optimizer_context, True
                )
            )
            for child in self.root_expr.children:
                child_expr = self.optimizer_context.memo.groups[child].logical_exprs[0]
                self.optimizer_context.task_stack.push(
                    BottomUpRewrite(child_expr, self.rule_set, self.optimizer_context)
                )
            return
        valid_rules = []
        for rule in self.rule_set:
            if not self.root_expr.is_rule_explored(rule.rule_type) and rule.top_match(
                self.root_expr.opr
            ):
                valid_rules.append(rule)

        # sort the rules by promise
        sorted(valid_rules, key=lambda x: x.promise())
        for rule in valid_rules:
            binder = Binder(self.root_expr, rule.pattern, self.optimizer_context.memo)
            for match in iter(binder):
                if not rule.check(match, self.optimizer_context):
                    continue
                logger.info(
                    "In BottomUp, Rule {} matched for {}".format(rule, self.root_expr)
                )
                after = rule.apply(match, self.optimizer_context)
                new_expr = self.optimizer_context.replace_expression(
                    after, self.root_expr.group_id
                )
                logger.info("After rewiting {}".format(self.root_expr))
                self.optimizer_context.task_stack.push(
                    BottomUpRewrite(new_expr, self.rule_set, self.optimizer_context)
                )
            self.root_expr.mark_rule_explored(rule.rule_type)


class OptimizeExpression(OptimizerTask):
    def __init__(
        self,
        root_expr: GroupExpression,
        optimizer_context: OptimizerContext,
        explore: bool,
    ):
        self.root_expr = root_expr
        self.explore = explore
        super().__init__(optimizer_context, OptimizerTaskType.OPTIMIZE_EXPRESSION)

    def execute(self):
        all_rules = RulesManager().logical_rules
        # if exploring, we don't need to consider implementation rules
        if not self.explore:
            all_rules.extend(RulesManager().implementation_rules)

        valid_rules = []
        for rule in all_rules:
            if rule.top_match(self.root_expr.opr):
                valid_rules.append(rule)

        sorted(valid_rules, key=lambda x: x.promise())

        for rule in valid_rules:
            # apply the rule
            self.optimizer_context.task_stack.push(
                ApplyRule(rule, self.root_expr, self.optimizer_context, self.explore)
            )

            # explore the input group if necessary
            for idx, child in enumerate(rule.pattern.children):
                if len(child.children):
                    child_grp_id = self.root_expr.children[idx]
                    group = self.optimizer_context.memo.get_group_by_id(child_grp_id)
                    self.optimizer_context.task_stack.push(
                        ExploreGroup(group, self.optimizer_context)
                    )


class ApplyRule(OptimizerTask):
    """apply a transformation or implementation rule"""

    def __init__(
        self,
        rule: Rule,
        root_expr: GroupExpression,
        optimizer_context: OptimizerContext,
        explore: bool,
    ):
        self.rule = rule
        self.root_expr = root_expr
        self.explore = explore
        super().__init__(optimizer_context, OptimizerTaskType.APPLY_RULE)

    def execute(self):
        # return if already explored
        if self.root_expr.is_rule_explored(self.rule.rule_type):
            return
        binder = Binder(self.root_expr, self.rule.pattern, self.optimizer_context.memo)
        for match in iter(binder):
            if not self.rule.check(match, self.optimizer_context):
                continue
            after = self.rule.apply(match, self.optimizer_context)
            new_expr = self.optimizer_context.add_opr_to_group(
                after, self.root_expr.group_id
            )

            if new_expr.is_logical():
                # optimize expressions
                self.optimizer_context.task_stack.push(
                    OptimizeExpression(new_expr, self.optimizer_context, self.explore)
                )
            else:
                # cost the physical expressions
                self.optimizer_context.task_stack.push(
                    OptimizeInputs(new_expr, self.optimizer_context)
                )

        self.root_expr.mark_rule_explored(self.rule.rule_type)


class OptimizeGroup(OptimizerTask):
    def __init__(self, group: Group, optimizer_context: OptimizerContext):
        self.group = group
        super().__init__(optimizer_context, OptimizerTaskType.OPTIMIZE_GROUP)

    def execute(self):
        # Todo: Get the property from the context
        if self.group.get_best_expr(PropertyType.DEFAULT):
            return

        # optimize all the logical exprs with the same context
        for expr in self.group.logical_exprs:
            self.optimizer_context.task_stack.push(
                OptimizeExpression(expr, self.optimizer_context, explore=False)
            )

        # cost all the physical exprs with the same context
        for expr in self.group.physical_exprs:
            self.optimizer_context.task_stack.push(
                OptimizeInputs(expr, self.optimizer_context)
            )


class OptimizeInputs(OptimizerTask):
    def __init__(self, root_expr: GroupExpression, optimizer_context: OptimizerContext):
        self.root_expr = root_expr
        super().__init__(optimizer_context, OptimizerTaskType.OPTIMIZE_INPUTS)

    def execute(self):
        cost = 0
        memo = self.optimizer_context.memo
        grp = memo.get_group_by_id(self.root_expr.group_id)
        for child_id in self.root_expr.children:
            child_grp = memo.get_group_by_id(child_id)
            if child_grp.get_best_expr(PropertyType.DEFAULT):
                cost += child_grp.get_best_expr_cost(PropertyType.DEFAULT)
            else:
                self.optimizer_context.task_stack.push(
                    OptimizeInputs(self.root_expr, self.optimizer_context)
                )
                self.optimizer_context.task_stack.push(
                    OptimizeGroup(child_grp, self.optimizer_context)
                )
                return

        cost += self.optimizer_context.cost_model.calculate_cost(self.root_expr)
        grp.add_expr_cost(self.root_expr, PropertyType.DEFAULT, cost)


class ExploreGroup(OptimizerTask):
    """
    Derive all logical group-expression for matching a pattern
    """

    def __init__(self, group: Group, optimizer_context: OptimizerContext):
        self.group = group
        super().__init__(optimizer_context, OptimizerTaskType.EXPLORE_GROUP)

    def execute(self):
        # return if the group is already explored
        if self.group.is_explored():
            return

        # explore all the logical expression
        for expr in self.group.logical_exprs:
            self.optimizer_context.task_stack.push(
                OptimizeExpression(expr, self.optimizer_context, explore=True)
            )

        # mark the group explored
        self.group.mark_explored()
