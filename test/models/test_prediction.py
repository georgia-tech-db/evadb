import unittest

import numpy as np

from src.models.inference.classifier_prediction import Prediction
from src.models.storage.batch import FrameBatch
from src.models.storage.frame import Frame

NUM_FRAMES = 10


class PredictionTest(unittest.TestCase):

    def test_should_check_if_batch_frames_equivalent_to_number_of_predictions(
            self):
        batch = FrameBatch(frames=[Frame(1, np.ones((1, 1)), None)], info=None)
        predictions = []
        scores = []
        self.assertRaises(AssertionError,
                          lambda x=None:
                          Prediction.predictions_from_batch_and_lists(
                              batch, predictions, scores))

    def test_should_check_if_batch_frames_equivalent_to_number_of_scores(self):
        batch = FrameBatch(frames=[Frame(1, np.ones((1, 1)), None)], info=None)
        predictions = [['A', 'B']]
        scores = []
        self.assertRaises(AssertionError,
                          lambda x=None:
                          Prediction.predictions_from_batch_and_lists(
                              batch, predictions, scores))

    def test_should_check_if_batch_frames_equivalent_to_no_of_boxes_if_given(
            self):
        batch = FrameBatch(frames=[Frame(1, np.ones((1, 1)), None)], info=None)
        predictions = [['A', 'B']]
        scores = [[1, 1]]
        boxes = []
        self.assertRaises(AssertionError,
                          lambda x=None:
                          Prediction.predictions_from_batch_and_lists(
                              batch, predictions, scores,
                              boxes=boxes))

    def test_should_return_list_of_predictions_for_each_frame_in_batch(self):
        batch = FrameBatch(frames=[Frame(1, np.ones((1, 1)), None)], info=None)
        predictions = [['A', 'B']]
        scores = [[1, 1]]
        expected = [Prediction(batch.frames[0], predictions[0], scores[0])]
        actual = Prediction.predictions_from_batch_and_lists(batch,
                                                             predictions,
                                                             scores)
        self.assertEqual(expected,
                         actual)
