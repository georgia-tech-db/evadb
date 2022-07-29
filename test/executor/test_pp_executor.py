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
import unittest
from test.executor.utils import DummyExecutor
from test.util import create_dataframe

from eva.executor.pp_executor import PPExecutor
from eva.models.storage.batch import Batch


class PPScanExecutorTest(unittest.TestCase):
    def test_should_return_only_frames_satisfy_predicate(self):
        dataframe = create_dataframe(3)
        batch = Batch(frames=dataframe)
        expression = type(
            "AbstractExpression", (), {"evaluate": lambda x: [False, False, True]}
        )

        plan = type("PPScanPlan", (), {"predicate": expression})
        predicate_executor = PPExecutor(plan)
        predicate_executor.append_child(DummyExecutor([batch]))

        expected = batch[[2]]
        filtered = list(predicate_executor.exec())[0]
        self.assertEqual(expected, filtered)
