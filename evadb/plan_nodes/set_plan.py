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
from typing import Any
from evadb.plan_nodes.abstract_plan import AbstractPlan
from evadb.plan_nodes.types import PlanOprType


class SetPlan(AbstractPlan):
    def __init__(self, config_name: str, config_value: Any):
        self.config_name = config_name
        self.config_value = config_value
        super().__init__(PlanOprType.SET)

    @property
    def config_name(self):
        return self.config_name

    @property
    def config_value(self):
        return self.config_value

    def __str__(self):
        return "SetPlan(config_name={}, \
            config_value={})".format(
            self.config_name, self.config_value
        )

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.config_name, self.config_value))
