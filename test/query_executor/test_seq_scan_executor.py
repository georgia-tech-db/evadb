import unittest

import numpy as np

from src.models.inference.classifier_prediction import Prediction
from src.models.storage.batch import FrameBatch
from src.models.storage.frame import Frame
from src.query_executor.seq_scan_executor import SequentialScanExecutor
from ..query_executor.utils import DummyExecutor


class SeqScanExecutorTest(unittest.TestCase):

    def test_should_return_only_frames_satisfy_predicate(self):
        frame_1 = Frame(1, np.ones((1, 1)), None)
        frame_2 = Frame(1, 2 * np.ones((1, 1)), None)
        frame_3 = Frame(1, 3 * np.ones((1, 1)), None)
        outcome_1 = Prediction(frame_1, ["car", "bus"], [0.5, 0.6])
        outcome_2 = Prediction(frame_2, ["bus"], [0.5, 0.6])
        outcome_3 = Prediction(frame_3, ["car", "train"], [0.5, 0.6])
        batch = FrameBatch(frames=[
            frame_1,
            frame_2,
            frame_3,
        ], info=None, outcomes={
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

        expected = FrameBatch(frames=[frame_3], info=None,
                              outcomes={"test": [outcome_3]})
        filtered = list(predicate_executor.next())[0]
        self.assertEqual(expected, filtered)

    def test_should_return_all_frames_when_no_predicate_is_applied(self):
        frame_1 = Frame(1, np.ones((1, 1)), None)
        frame_2 = Frame(1, 2 * np.ones((1, 1)), None)
        frame_3 = Frame(1, 3 * np.ones((1, 1)), None)
        outcome_1 = Prediction(frame_1, ["car", "bus"], [0.5, 0.6])
        outcome_2 = Prediction(frame_2, ["bus"], [0.5, 0.6])
        outcome_3 = Prediction(frame_3, ["car", "train"], [0.5, 0.6])
        batch = FrameBatch(frames=[
            frame_1,
            frame_2,
            frame_3,
        ], info=None, outcomes={
            "test": [
                outcome_1,
                outcome_2,
                outcome_3
            ]
        })

        plan = type("ScanPlan", (), {"predicate": None})
        predicate_executor = SequentialScanExecutor(plan)
        predicate_executor.append_child(DummyExecutor([batch]))

        expected = FrameBatch(frames=[frame_1, frame_2, frame_3], info=None,
                              outcomes={"test": [outcome_1, outcome_2,
                                                 outcome_3]})
        filtered = list(predicate_executor.next())[0]
        self.assertEqual(expected, filtered)
