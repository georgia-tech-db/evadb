# coding=utf-8
# Copyright 2018-2023 EvaDB
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

from typing import Any

from evadb.parser.statement import AbstractStatement
from evadb.parser.types import StatementType


class SetStatement(AbstractStatement):
    def __init__(self, config_name: str, config_value: Any):
        super().__init__(StatementType.SET)
        self._config_name = config_name
        self._config_value = config_value

    @property
    def config_name(self):
        return self._config_name

    @property
    def config_value(self):
        return self._config_value

    def __str__(self):
        return f"SET {str(self.config_name)} = {str(self.config_value)}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SetStatement):
            return False
        return (
            self.config_name == other.config_name
            and self.config_value == other.config_value
        )

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.config_name, self.config_value))
