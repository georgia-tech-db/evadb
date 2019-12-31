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
"""
This file gives interface to all query optimizer modules
If any issues arise please contact jaeho.bang@gmail.com

@Jaeho Bang
"""

from abc import ABCMeta, abstractmethod

"""
Initial Design Thoughts:
Query Optimizer by definition should perform two tasks:
1. analyze Structered Query Language
2. Determine efficient execution mechanisms (plans)

"""


class QOTemplate(metaclass=ABCMeta):

    @abstractmethod
    def executeQueries(self, queries: list) -> list:
        """
        Query Optimizer by definition should perform two tasks:
        1. Analyze given Structured Query Language (SQL)
        2. Determine efficient execution mechanisms/plans
        :param queries: input queries / query
        :return: output plans / plan that can be understood by the system
        """
