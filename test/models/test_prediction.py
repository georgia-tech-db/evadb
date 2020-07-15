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

import numpy as np

from src.models.inference.classifier_prediction import Prediction
from src.models.storage.batch import Batch
from src.models.storage.frame import Frame

NUM_FRAMES = 10


class PredictionTest(unittest.TestCase):

    def test_should_check_if_batch_frames_equivalent_to_number_of_predictions(
            self):
        batch = Batch(frames=[Frame(1, np.ones((1, 1)), None).asdict()])
        predictions = []
        scores = []
        self.assertRaises(AssertionError,
                          lambda x=None:
                          Prediction.predictions_from_batch_and_lists(
                              batch, predictions, scores))

    def test_should_check_if_batch_frames_equivalent_to_number_of_scores(self):
        batch = Batch(frames=[Frame(1, np.ones((1, 1)), None).asdict()])
        predictions = [['A', 'B']]
        scores = []
        self.assertRaises(AssertionError,
                          lambda x=None:
                          Prediction.predictions_from_batch_and_lists(
                              batch, predictions, scores))

    def test_should_check_if_batch_frames_equivalent_to_no_of_boxes_if_given(
            self):
        batch = Batch(frames=[Frame(1, np.ones((1, 1)), None).asdict()])
        predictions = [['A', 'B']]
        scores = [[1, 1]]
        boxes = []
        self.assertRaises(AssertionError,
                          lambda x=None:
                          Prediction.predictions_from_batch_and_lists(
                              batch, predictions, scores,
                              boxes=boxes))

    def test_should_return_list_of_predictions_for_each_frame_in_batch(self):
        batch = Batch(frames=[Frame(1, np.ones((1, 1)), None).asdict()])
        predictions = [['A', 'B']]
        scores = [[1, 1]]
        expected = [Prediction(batch.frames, predictions[0], scores[0])]
        actual = Prediction.predictions_from_batch_and_lists(batch,
                                                             predictions,
                                                             scores)
        self.assertEqual(expected,
                         actual)
