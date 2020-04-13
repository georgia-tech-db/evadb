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
import unittest

from src.executor.seq_scan_executor import SequentialScanExecutor
from src.models.inference.classifier_prediction import Prediction
from src.models.storage.batch import FrameBatch
from test.util import create_dataframe
from ..executor.utils import DummyExecutor


class SeqScanExecutorTest(unittest.TestCase):

    def test_should_return_only_frames_satisfy_predicate(self):
        dataframe = create_dataframe(3)

        outcome_1 = Prediction(dataframe.iloc[0], ["car", "bus"], [0.5, 0.6])
        outcome_2 = Prediction(dataframe.iloc[1], ["bus"], [0.5, 0.6])
        outcome_3 = Prediction(dataframe.iloc[2], ["car", "train"], [0.5, 0.6])
        batch = FrameBatch(frames=dataframe, outcomes={
            "test": [
                outcome_1,
                outcome_2,
                outcome_3
            ]
        })
        expression = type("AbstractExpression", (), {"evaluate": lambda x: [
            False, False, True]})

        plan = type("ScanPlan", (), {"predicate": expression})
        predicate_executor = SequentialScanExecutor(plan)
        predicate_executor.append_child(DummyExecutor([batch]))

        expected = batch[[2]]
        filtered = list(predicate_executor.exec())[0]
        self.assertEqual(expected, filtered)

    def test_should_return_all_frames_when_no_predicate_is_applied(self):
        dataframe = create_dataframe(3)

        outcome_1 = Prediction(dataframe.iloc[0], ["car", "bus"], [0.5, 0.6])
        outcome_2 = Prediction(dataframe.iloc[1], ["bus"], [0.5, 0.6])
        outcome_3 = Prediction(dataframe.iloc[2], ["car", "train"], [0.5, 0.6])
        batch = FrameBatch(frames=dataframe, outcomes={
            "test": [
                outcome_1,
                outcome_2,
                outcome_3
            ]
        })

        plan = type("ScanPlan", (), {"predicate": None})
        predicate_executor = SequentialScanExecutor(plan)
        predicate_executor.append_child(DummyExecutor([batch]))

        filtered = list(predicate_executor.exec())[0]
        self.assertEqual(batch, filtered)
