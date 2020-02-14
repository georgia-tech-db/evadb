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
from typing import List

from src.expression.abstract_expression import AbstractExpression
from src.planner.types import PlanNodeType


class InsertPlan(AbstractPlan):
    """
    This plan is used for storing information required for insert
    operations.

    Arguments:
        video_id{int} -- video metadata id to insert into
        column_list{List[int]} -- list of column metadata ids
        value_list{List[AbstractExpression]} -- list of abstract expression
                                                for the values to insert
    """

    def __init__(self, video_id: int, column_ids: List[int],
                 value_list: List[AbstractExpression]):
        super().__init__(PlanNodeType.INSERT)
        self._video_id = video_id
        self._columns_ids = column_ids
        self._value_list = value_list

    @property
    def video_id(self):
        return self._video_id

    @property
    def column_ids(self):
        return self._columns_ids

    @property
    def value_list(self):
        return self._value_list
