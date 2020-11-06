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
from enum import IntEnum, auto
from src.optimizer.rules.rules import RulesManager
from src.optimizer.operators import Operator
from src.optimizer.group_expression import GroupExpression
from src.optimizer.optimizer_context import OptimizerContext
from src.optimizer.binder import Binder
from src.optimizer.property import PropertyType
from src.utils.logging_manager import LoggingManager, LoggingLevel

class OptimizerTaskType(IntEnum):
    """Manages Enum for all the supported optimizer tasks
    """
    TOP_DOWN_REWRITE = auto()
    BOTTOM_UP_REWRITE = auto()
    OPTIMIZE_EXPRESSION = auto()
    OPTIMIZE_GROUP = auto()
    OPTIMIZE_INPUTS = auto()


class OptimizerTask:
    def __init__(self, root_expr, root_id, optimizer_context, task_type: OptimizerTaskType):
        self._root_expr = root_expr
        self._root_id = root_id
        self._task_type = task_type
        self._optimizer_context = optimizer_context

    @property
    def root_expr(self):
        return self._root_expr

    @property
    def root_id(self):
        return self._root_id

    @property
    def task_type(self):
        return self._task_type

    @property
    def optimizer_context(self):
        return self._optimizer_context

    @root_expr.setter
    def root_expr(self, expr):
        self.root_expr = expr

    def execute(self):
        raise NotImplementedError


class TopDownRewrite(OptimizerTask):
    def __init__(self, root_expr: GroupExpression,
                 optimizer_context: OptimizerContext):
        super().__init__(root_expr, root_expr.group_id,
                         optimizer_context, OptimizerTaskType.TOP_DOWN_REWRITE)

    @property
    def root_expr(self):
        return self._root_expr

    @root_expr.setter
    def root_expr(self, expr):
        self._root_expr = expr

    def execute(self):
        """We apply rewrite rules in a top down fashion.
        Right now we are applying rules aggressively. Later
        when we have more rules it might be a better idea to
        push optimization task to a queue.
        """
        rewrite_rules = RulesManager().rewrite_rules
        valid_rules = []
        for rule in rewrite_rules:
            if not self.root_expr.is_rule_explored(rule.rule_type) and rule.top_match(self.root_expr.opr):
                valid_rules.append(rule)

        # sort the rules by promise
        valid_rules = sorted(valid_rules, key=lambda x: x.promise(), reverse=True)
        for rule in valid_rules:
            binder = Binder(self.root_expr, rule.pattern,
                            self.optimizer_context.memo)
            for match in iter(binder):
                if not rule.check(self.root_expr.group_id,
                                  self.optimizer_context):
                    continue
                LoggingManager().log('In TopDown, Rule {} matched for {}'
                                     .format(rule, self.root_expr),
                                     LoggingLevel.DEBUG)
                after = rule.apply(match, self.optimizer_context)
                new_expr = self.optimizer_context.xform_opr_to_group_expr(after, False)
                new_expr.mark_rule_explored(rule.rule_type)
                self.optimizer_context.memo.replace_group_expr(
                    self.root_expr.group_id, new_expr)
                self.root_expr = new_expr
                LoggingManager().log('After rewiting {}'.format(self.root_expr),
                                     LoggingLevel.DEBUG)
                self.optimizer_context.task_stack.push(TopDownRewrite(
                    self.root_expr, self.optimizer_context))

        for child in self.root_expr.children:
            child_expr = self.optimizer_context.memo.get_group(
                child).logical_exprs[0]
            self.optimizer_context.task_stack.push(TopDownRewrite(
                child_expr, self.optimizer_context))

class BottomUpRewrite(OptimizerTask):
    def __init__(self, root_expr: GroupExpression,
                 optimizer_context: OptimizerContext, children_explored = False):
        super().__init__(root_expr, root_expr.group_id,
                         optimizer_context, OptimizerTaskType.BOTTOM_UP_REWRITE)
        self._children_explored = children_explored

    @property
    def root_expr(self):
        return self._root_expr

    @root_expr.setter
    def root_expr(self, expr):
        self._root_expr = expr

    def execute(self):
        if not self._children_explored:
            self.optimizer_context.task_stack.push(BottomUpRewrite(
                    self.root_expr, self.optimizer_context, True))
            for child in self.root_expr.children:
                child_expr = self.optimizer_context.memo.get_group(
                    child).logical_exprs[0]
                self.optimizer_context.task_stack.push(BottomUpRewrite(
                    child_expr, self.optimizer_context))
            return
        rewrite_rules = RulesManager().rewrite_rules
        valid_rules = []
        for rule in rewrite_rules:
            if not self.root_expr.is_rule_explored(rule.rule_type) and rule.top_match(self.root_expr.opr):
                valid_rules.append(rule)

        # sort the rules by promise
        sorted(valid_rules, key=lambda x: x.promise(), reverse=True)
        for rule in valid_rules:
            binder = Binder(self.root_expr, rule.pattern,
                            self.optimizer_context.memo)
            for match in iter(binder):
                if not rule.check(self.root_expr.group_id,
                                  self.optimizer_context):
                    continue
                LoggingManager().log('In BottomUp, Rule {} matched for {}'
                                     .format(rule, self.root_expr),
                                     LoggingLevel.DEBUG)
                after = rule.apply(match, self.optimizer_context)
                new_expr = self.optimizer_context.xform_opr_to_group_expr(after, False)
                new_expr.mark_rule_explored(rule.rule_type)
                self.optimizer_context.memo.replace_group_expr(
                    self.root_expr.group_id, new_expr)
                self.root_expr = new_expr
                LoggingManager().log('After rewiting {}'.format(self.root_expr),
                                     LoggingLevel.DEBUG)
                self.optimizer_context.task_stack.push(BottomUpRewrite(
                    new_expr, self.optimizer_context))

class OptimizeExpression(OptimizerTask):
    def __init__(self, root_expr, optimizer_context):
        super().__init__(root_expr, root_expr.group_id,
                         optimizer_context, OptimizerTaskType.OPTIMIZE_EXPRESSION)

    def execute(self):
        implementation_rules = RulesManager().implementation_rules
        valid_rules = []
        for rule in implementation_rules:
            if rule.top_match(self.root_expr.opr):
                valid_rules.append(rule)

        sorted(valid_rules, key=lambda x: x.promise(), reverse=True)
        for rule in valid_rules:
            binder = Binder(self.root_expr, rule.pattern,
                            self.optimizer_context.memo)
            for match in iter(binder):
                if not rule.check(self.root_expr.group_id,
                                  self.optimizer_context):
                    continue
                LoggingManager().log('In Optimize physical expression,'
                                     'Rule {} matched for {}'
                                     .format(rule, self.root_expr),
                                     LoggingLevel.DEBUG)
                after = rule.apply(match, self.optimizer_context)
                new_expr = GroupExpression(
                    after, self.root_expr.group_id, self.root_expr.children)
                LoggingManager().log('After rewiting {}'.format(new_expr),
                                     LoggingLevel.DEBUG)
                self.optimizer_context.memo.add_group_expr(new_expr)
                # Optimize inputs for this physical expr
                self.optimizer_context.task_stack.push(OptimizeInputs(new_expr, self.optimizer_context))

            # Optimize the child groups
            for child_id in self.root_expr.children:
                child_expr = self.optimizer_context.task_stack.push(
                    OptimizeGroup(child_id, self.optimizer_context))


class OptimizeGroup(OptimizerTask):
    def __init__(self, root_id, optimizer_context):
        super().__init__(None, root_id,
                         optimizer_context, OptimizerTaskType.OPTIMIZE_GROUP)

    def execute(self):
        grp = self.optimizer_context.memo.get_group(self.root_id)
        for expr in grp.logical_exprs:
            self.optimizer_context.task_stack.push(OptimizeExpression(expr, self.optimizer_context))

        for expr in grp.physical_exprs:
            self.optimizer_context.task_stack.push(OptimizeInputs(expr, self.optimizer_context))


class OptimizeInputs(OptimizerTask):
    def __init__(self, root_expr, optimizer_context):
        super().__init__(root_expr, root_expr.group_id,
                         optimizer_context, OptimizerTaskType.OPTIMIZE_INPUTS)

    def execute(self):
            cost = 0
            grp = self.optimizer_context.memo.get_group(self.root_id)
            for child_id in self.root_expr.children:
                child_grp = self.optimizer_context.memo.get_group(child_id)
                if child_grp.get_best_expr(PropertyType.DEFAULT):
                    cost += child_grp.get_best_expr_cost(PropertyType.DEFAULT)
                else:
                    self.optimizer_context.task_stack.push(OptimizeInputs(self.root_expr, self.optimizer_context))
                    self.optimizer_context.task_stack.push(
                        OptimizeGroup(child_id, self.optimizer_context))
                    return

            grp.add_expr_cost(self.root_expr, PropertyType.DEFAULT, cost)

