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
from evadb.expression.constant_value_expression import ConstantValueExpression
from evadb.plan_nodes.abstract_plan import AbstractPlan
from evadb.plan_nodes.types import PlanOprType
from typing import List
from evadb.expression.abstract_expression import AbstractExpression
from evadb.expression.tuple_value_expression import TupleValueExpression


class StringAggPlan(AbstractPlan):
    """
    This plan is used for storing information required for group by
    operations.

    Arguments:
        string_agg_clause: (TupleValueExpression, ConstantValueExpression, List[(TupleValueExpression, EnumInt), ...])
            First element represents columns to aggregate, second is a constant string representing separator,
            third element is the optional order_by expression
    """

    def __init__(self, string_agg_clause):
        self._string_agg_clause = string_agg_clause
        super().__init__(PlanOprType.STRING_AGG)


    @property
    def columns(self):
        if isinstance(self._string_agg_clause[0], List):
            return self._string_agg_clause[0]
        else:
            return [self._string_agg_clause[0]]

    @property
    def separator(self):
        return self._string_agg_clause[1]

    @property
    def order_by(self):
        if len(self._string_agg_clause) == 3:
            return self._string_agg_clause[2]
        else:
            return None

    @property
    def string_agg_clause(self):
        return self._string_agg_clause

    def __str__(self):
        return "StringAggPlan(string_agg_clause={})".format(self._string_agg_clause)

    def __hash__(self) -> int:
        if isinstance(self.string_agg_clause[0], List):
            return hash((super().__hash__(), tuple(self.string_agg_clause[0])))
        else:
            return hash((super().__hash__(), tuple(self.string_agg_clause)))
