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


class BasePrediction(ABC):
    """
    Base class for any type of prediction from model.
    Subclasses should override the comparators which are suitable for them.
    All the comparators default to False.
    """

    def __eq__(self, other):
        """
        Checks if prediction is equal to the element
        Arguments:
            element (object): Check if element is equivalent
        Returns:
            bool (True if equal else False)
        """
        return False

    def __contains__(self, element) -> bool:
        """
        Checks if the prediction contains the element
        Arguments:
            element (object): Element to be checked
        Returns:
            bool (True if contains else False)
        """
        return False

    def __gt__(self, other):
        """
        Checks for > operation
        Arguments:
            other (Any): Element to be checked
        Returns:
            bool (True if greater)
        """
        return False

    def __ge__(self, other):
        """
        Checks for >= operation
        Arguments:
            other (Any): Element to be checked
        Returns:
            bool (True if greater)
        """
        return self > other and self == other

    def __lt__(self, other):
        """
        Checks for < operation
        Arguments:
            other (Any): Element to be checked
        Returns:
            bool (True if greater)
        """
        return False

    def __le__(self, other):
        """
        Checks for <= operation
        Arguments:
            other (Any): Element to be checked
        Returns:
            bool (True if less than or equal)
        """
        return self < other and self == other

    def __ne__(self, other):
        """
        Checks for not equals operation
        Arguments:
            other (Any): Element to be checked
        Returns:
            bool (True if not equal)
        """
        return not (self == other)
