import os
import unittest
import cv2
import sys
import numpy as np

from src.models import Frame, FrameBatch
from src.udfs.depth_estimator import DepthEstimator


class DepthEstimatorTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_path = os.path.dirname(os.path.abspath(__file__))

    def _load_image(self, path):
        img = cv2.imread(path)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    def test_should_return_batches_equivalent_to_number_of_frames(self):
        frame_1 = Frame(1, self._load_image(
            os.path.join(self.base_path, 'data', 'kitti_car_1.png')), None)
        frame_2 = Frame(1, self._load_image(
            os.path.join(self.base_path, 'data', 'kitti_car_2.png')), None)
        frame_batch = FrameBatch([frame_1, frame_2], None)
        estimator = DepthEstimator()
        result = estimator.process_frames(frame_batch)
        self.assertEqual(len(result), 2)
        self.assertTrue(np.array_equal(result[0].frame.data, frame_1.data))
        self.assertTrue(np.array_equal(result[1].frame.data, frame_2.data))
        assert result[0].depth is not None
        assert result[0].segm is not None
        assert result[1].depth is not None
        assert result[1].segm is not None
