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
from src.optimizer.generators.base import Generator
from src.optimizer.operators import LogicalCreateUDF, Operator
from src.planner.create_udf_plan import CreateUDFPlan


class CreateUDFGenerator(Generator):
    def __init__(self):
        self._name = None
        self._inputs = None
        self._outputs = None
        self._if_not_exists = None
        self._impl_path = None
        self._udf_type = None

    def _visit_logical_create_udf(self, operator: LogicalCreateUDF):
        self._name = operator.name
        self._inputs = operator.inputs
        self._outputs = operator.outputs
        self._if_not_exists = operator.if_not_exists
        self._impl_path = operator.impl_path
        self._udf_type = operator.udf_type
    
    def _visit(self, operator: Operator):
        if isinstance(operator, LogicalCreateUDF):
            self._visit_logical_create_udf(operator)

    def build(self, operator: Operator):
        self.__init__()
        self._visit(operator)
        create_udf_plan = CreateUDFPlan(
            self._name,
            self._if_not_exists,
            self._inputs, self._outputs, self._impl_path, self._udf_type)
        return create_udf_plan
