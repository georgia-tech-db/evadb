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

from eva.planner.abstract_plan import AbstractPlan
from eva.planner.types import PlanOprType
from eva.parser.table_ref import TableRef

from typing import List


class ApplyBlurPlan(AbstractPlan):
    """
    This plan is used for storing information required for applying a blur.
    """

    def __init__(self):
        super().__init__(PlanOprType.APPLY_BLUR)
