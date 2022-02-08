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

from eva.parser.statement import AbstractStatement

from eva.parser.types import StatementType


class ApplyBlurStatement(AbstractStatement):
    def __init__(self, query: SelectStatement):
        super().__init__(StatementType.APPLY_BLUR)
        self._query = query

    def __str__(self) -> str:
        print_str = "APPLY_BLUR {}".format(self._query)
        return print_str
    
    @property
    def query(self):
        return self._query

    def __eq__(self, other):
        if not isinstance(other, ApplyBlurStatement):
            return False
        print(self)
        print(other)
        return (self.query == other.query)
