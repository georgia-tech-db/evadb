import unittest

import numpy as np

from src.models import FrameBatch, Frame, Prediction, Predicate
from src.query_executor.seq_scan_executor import SequentialScanExecutor


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
        predicate = Predicate(name="test",
                              predicate=lambda prediction: prediction.eq(
                                  "car") and not prediction.eq("bus"))
        plan = type("ScanPlan", (), {"predicate": predicate})
        predicate_executor = SequentialScanExecutor(plan)

        expected = FrameBatch(frames=[frame_3], info=None,
                              outcomes={"test": [outcome_3]})
        filtered = predicate_executor.execute(batch)
        self.assertEqual(expected, filtered)
