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
from eva.expression.abstract_expression import AbstractExpression
from eva.expression.function_expression import FunctionExpression
from eva.parser.alias import Alias
from eva.plan_nodes.abstract_plan import AbstractPlan
from eva.plan_nodes.types import PlanOprType


class ExtractObjectPlan(AbstractPlan):
    """Extract object plan

    Args:
        expr: the extract object expression
        detector: the object detector to use for extracting objects
        tracker: the object tracking algorithm
        alias: the alias for the `expr`
        do_unnest: whether to return results as one object per row or one row for each frame
    """

    def __init__(
        self,
        expr: AbstractExpression,
        detector: FunctionExpression,
        tracker: FunctionExpression,
        tracker_args: dict,
        alias: Alias,
        do_unnest: bool,
    ):
        super().__init__(PlanOprType.EXTRACT_OBJECT)
        self.expr = expr
        self.detector = detector
        self.tracker = tracker
        self.tracker_args = tracker_args
        self.alias = alias
        self.do_unnest = do_unnest

    def __str__(self) -> str:
        return (
            f"ExtractObjectPlan({self.expr.children[0]}, {self.detector}"
            f", {self.tracker} )"
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.expr,
                self.detector,
                self.tracker,
                self.tracker_args,
                self.alias,
                self.do_unnest,
            )
        )
