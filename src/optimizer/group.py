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

from src.optimizer.operators import Operator

from typing import List


class Group:
    def __init__(self, group_id: int,
                 logical_exprs: List[Operator] = None,
                 physical_exprs: List[Operator] = None):
        self._group_id = group_id
        self._logical_exprs = logical_exprs
        self._physical_exprs = physical_exprs

    @property
    def group_id(self):
        return self._group_id

    def add_logical_expr(self, opr: Operator):
        self._logical_exprs.append(opr)

    def add_physical_expr(self, opr: Operator):
        self._physical_exprs.append(opr)
