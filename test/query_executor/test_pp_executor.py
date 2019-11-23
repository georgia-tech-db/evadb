import unittest

import numpy as np

from src.models.storage.batch import FrameBatch
from src.models.storage.frame import Frame
from src.query_executor.pp_executor import PPExecutor
from ..query_executor.utils import DummyExecutor


class PPScanExecutorTest(unittest.TestCase):

    def test_should_return_only_frames_satisfy_predicate(self):
        frame_1 = Frame(1, np.ones((1, 1)), None)
        frame_2 = Frame(1, 2 * np.ones((1, 1)), None)
        frame_3 = Frame(1, 3 * np.ones((1, 1)), None)
        batch = FrameBatch(frames=[
            frame_1,
            frame_2,
            frame_3,
        ], info=None)
        expression = type("AbstractExpression", (), {"evaluate": lambda x: [
            False, False, True]})

        plan = type("PPScanPlan", (), {"predicate": expression})
        predicate_executor = PPExecutor(plan)
        predicate_executor.append_child(DummyExecutor([batch]))

        expected = FrameBatch(frames=[frame_3], info=None)
        filtered = list(predicate_executor.next())[0]
        self.assertEqual(expected, filtered)
