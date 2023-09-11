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
import unittest

import pandas as pd
from mock import MagicMock

from evadb.executor.project_executor import ProjectExecutor
from evadb.models.storage.batch import Batch


class ProjectExecutorTest(unittest.TestCase):
    def test_should_return_expr_without_table_source(self):
        constant = Batch(pd.DataFrame([1]))
        expression = [
            type(
                "AbstractExpression",
                (),
                {
                    "evaluate": lambda x: constant,
                    "find_all": lambda expr: [],
                },
            )
        ]

        plan = type("ProjectPlan", (), {"predicate": None, "target_list": expression})
        proj_executor = ProjectExecutor(MagicMock(), plan)

        actual = list(proj_executor.exec())[0]
        self.assertEqual(constant, actual)


if __name__ == "__main__":
    unittest.main()
