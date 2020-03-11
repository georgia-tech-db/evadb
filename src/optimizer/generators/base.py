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
from abc import ABC, abstractmethod

from src.optimizer.operators import Operator
from src.planner.abstract_plan import AbstractPlan


class Generator(ABC):

    @abstractmethod
    def build(self, operator: Operator) -> AbstractPlan:
        """
        Generates the physical plan from the Logical plan (Operator tree)

        Arguments:
            operator (Operator): the logical operator tree.

        Returns:
            `AbstractPlan`: the plan constructed by traversing the Operator
            tree.
        """
