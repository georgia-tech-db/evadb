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

from typing import List


class Alias:
    def __init__(self, alias_name: str, col_names: List[str] = []) -> None:
        self._alias_name = alias_name
        self._col_names = col_names

    @property
    def alias_name(self):
        return self._alias_name

    @property
    def col_names(self):
        return self._col_names

    def __hash__(self) -> int:
        return hash((self.alias_name, tuple(self.col_names)))

    def __eq__(self, other):
        if not isinstance(other, Alias):
            return False
        return self.alias_name == other.alias_name and self.col_names == other.col_names

    def __str__(self):
        msg = f"{self.alias_name}"
        if len(self.col_names) > 0:
            msg += f"({str(self.col_names)})"
        return msg
