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
from enum import IntEnum, auto


class PropertyType(IntEnum):
    # We don't have specific properties right now
    # default is a proxy to represent no specific properties
    DEFAULT = auto()


class Property:
    def __init__(self, property_type):
        self._property_type = property_type

    def property_type(self):
        return self._property_type

    def __eq__(self, other):
        return self.property_type == other.property_type

    def __hash__(self):
        return hash(self._property_type)
