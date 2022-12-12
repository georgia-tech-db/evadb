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

from eva.optimizer.operators import OperatorType


class Pattern:
    def __init__(self, opr_type: OperatorType):
        self._opr_type = opr_type
        self._chilren = []

    def append_child(self, child: Pattern):
        self._chilren.append(child)

    @property
    def children(self):
        return self._chilren

    @property
    def opr_type(self):
        return self._opr_type
