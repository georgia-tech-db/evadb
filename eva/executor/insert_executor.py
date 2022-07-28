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
from eva.executor.abstract_executor import AbstractExecutor
from eva.planner.insert_plan import InsertPlan


class InsertExecutor(AbstractExecutor):
    def __init__(self, node: InsertPlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self):
        """
        Based on the table it constructs a valid tuple using the values
        provided.
        Right now we assume there are no missing values
        """
        raise NotImplementedError
