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


from abc import ABC
from src.planner.types import PlanOprType
from typing import List


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
    def parent(self, node: 'AbstractPlan'):
        """sets parent of current node

        Arguments:
            node {AbstractPlan} -- parent node
        """
        # remove if we don't allow setter function
        # parent can be constructor only job
        self._parent = node

    @property
    def children(self) -> List['AbstractPlan']:
        """returns children list of current node

        Returns:
            List[AbstractPlan] -- children list
        """
        return self._children[:]

    @property
    def opr_type(self) -> PlanOprType:
        """
        Property used for returning the node type of Plan.

        Returns:
            PlanOprType: The node type corresponding to the plan
        """
        return self._opr_type

    def __str__(self, level=0):
        out_string = "\t" * level + '' + "\n"
        for child in self.children:
            out_string += child.__str__(level + 1)
        return out_string

    def is_logical(self):
        return False