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
from eva.planner.abstract_plan import AbstractPlan
from eva.planner.types import PlanOprType


class OrderByPlan(AbstractPlan):
    """
    This plan is used for storing information required for order by
    operations.

    Arguments:
        orderby_list: List[(TupleValueExpression, EnumInt), ...]
            A tuple of the column names string and the type of sort in the plan
    """

    def __init__(self, orderby_list):
        self._orderby_list = orderby_list
        super().__init__(PlanOprType.ORDER_BY)

    @property
    def columns(self):
        return [_[0] for _ in self._orderby_list]

    @property
    def sort_types(self):
        return [_[1] for _ in self._orderby_list]

    @property
    def orderby_list(self):
        return self._orderby_list

    def __str__(self):
        return "OrderByPlan(orderby_list={})".format(self._orderby_list)

    def __hash__(self) -> int:
        return hash((super().__hash__(), tuple(self._orderby_list)))
