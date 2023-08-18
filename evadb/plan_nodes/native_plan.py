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
from evadb.plan_nodes.abstract_plan import AbstractPlan
from evadb.plan_nodes.types import PlanOprType


class NativePlan(AbstractPlan):
    """
    This plan is used for pushing down query string directly to
    backend database engine.
    """

    def __init__(self, plan_type: PlanOprType, database_name: str, query_string: str):
        self._database_name = database_name
        self._query_string = query_string
        super().__init__(plan_type)

    @property
    def database_name(self):
        return self._database_name

    @property
    def query_string(self):
        return self._query_string

    def __str__(self):
        return "NativePlan(database_name={}, query_string={})".format(
            self._database_name,
            self._query_string,
        )

    def __hash__(self) -> int:
        return hash((super().__hash__(), self._database_name, self._query_string))


class SQLAlchemyPlan(NativePlan):
    def __init__(self, database_name: str, query_string: str):
        super().__init__(PlanOprType.SQLALCHEMY, database_name, query_string)
