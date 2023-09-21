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
import pandas as pd

from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.plan_nodes.set_plan import SetPlan


class SetExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: SetPlan):
        super().__init__(db, node)

    def exec(self, *args, **kwargs):
        # Get method implementation from the config.update_value
        self._config.update_value(
            category="default", key=SetPlan.config_name, value=SetPlan.config_value
        )
        pass
