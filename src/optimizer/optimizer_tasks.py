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


class OptimizerTaskType(IntEnum):
    """Manages Enum for all the supported optimizer tasks
    """
    TOP_DOWN_REWRITE = auto()


class OptimizerTask:
    def __init__(self, root_expr, optimizer_context, task_type: OptimizerTaskType):
        self._root_expr = root_expr
        self._task_type = task_type
        self._optimizer_context = optimizer_context

    @property
    def root_expr(self):
        return self._root_expr

    @property
    def task_type(self):
        return self._task_type

    @property
    def optimizer_context(self):
        return self._optimizer_context

    def execute(self):
        raise NotImplementedError

    def push_task(self, task):
        self.optimizer_context.task_stack.push_task(task)


class TopDownRewrite(OptimizerTask):
    def __init__(self, root_expr: GroupExpression,
                 optimizer_context: OptimizerContext):
        super().__init__(root_expr, optimizer_context, OptimizerTaskType.TOP_DOWN_REWRITE)

    def execute(self):
        """We apply rewrite rules in a top down fashion.
        Right now we are applying rules aggressively. Later
        when we have more rules it might be a better idea to 
        push optimization task to a queue.
        """

        rewrite_rules = RulesManager().rewrite_rules
        valid_rules = []
        for rule in rewrite_rules:
            if rule.top_match(self.root_expr.opr):
                valid_rules.append(rule)
        
        # sort the rules by promise
        sorted(valid_rules, key=lambda x: x.promise(), reverse=True)
        
        for rule in valid_rules:
            binder = Binder(self.root_expr, rule.pattern, self.optimizer_context.memo)
            for match in iter(binder):
                after = rule.apply(match, self.optimizer_context)
                new_expr = GroupExpression(after, self.root_expr.group_id)
                self.optimizer_context.memo.replace_group_expr(root_expr.group_id, new_expr)
                # self.push_task(TopDownRewrite(new_expr, self.optimizer_context))
                TopDownRewrite(new_expr, optimizer_context)

        # for child in grp_expr.children:
        #     # self.optimizer_context.task_stack.push_task(TopDownRewrite(child, self.optimizer_context))
