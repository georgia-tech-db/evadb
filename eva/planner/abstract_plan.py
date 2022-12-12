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
from abc import ABC, abstractmethod
from typing import List

from eva.planner.types import PlanOprType


class AbstractPlan(ABC):
    def __init__(self, opr_type):
        self._children = []
        self._parent = None
        self._opr_type = opr_type

    def append_child(self, child):
        """append node to children list

        Arguments:
            child {AbstractPlan} -- input child node
        """
        self._children.append(child)

    @property
    def parent(self):
        """Returns the parent of current node

        Returns:
            AbstractPlan -- parent node
        """
        return self._parent

    @parent.setter
    def parent(self, node: "AbstractPlan"):
        """sets parent of current node

        Arguments:
            node {AbstractPlan} -- parent node
        """
        # remove if we don't allow setter function
        # parent can be constructor only job
        self._parent = node

    @property
    def children(self) -> List["AbstractPlan"]:
        return self._children

    @property
    def opr_type(self) -> PlanOprType:
        """
        Property used for returning the node type of Plan.

        Returns:
            PlanOprType: The node type corresponding to the plan
        """
        return self._opr_type

    def clear_children(self):
        self.children.clear()

    def is_logical(self):
        return False

    @abstractmethod
    def __hash__(self) -> int:
        return hash(self.opr_type)

    @abstractmethod
    def __str__(self) -> str:
        return "AbstractPlan"

    def __copy__(self):
        # deepcopy the children
        cls = self.__class__
        result = cls.__new__(cls)
        for k, v in self.__dict__.items():
            if k == "_children":
                setattr(result, k, [])
            else:
                setattr(result, k, v)
        return result
