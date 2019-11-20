import os
import unittest
import cv2
import sys
import numpy as np

from src.models import Frame, FrameBatch
from src.udfs.depth_estimator import DepthEstimator


class DepthEstimatorTest(unittest.TestCase):
    """
        unit test class for  depth estimation model

        Arguments:
        unittest.TestCase

    """

    def __init__(self, *args, **kwargs):
        """
                      method to initialize the class object

                      Arguments:
                      args
                      kwargs

        """
        super().__init__(*args, **kwargs)
        self.base_path = os.path.dirname(os.path.abspath(__file__))


    def _load_image(self, path):
        """
               method to load the image from a given input path

               Arguments:
               path : path where image file is located

        """
        img = cv2.imread(path)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


    def test_should_return_batches_equivalent_to_number_of_frames(self):
        """
                Unit test method which creates a batch of frames, sends it for model prediction.
                It then checks if the returned object size is as expected.

        """

        # create two frames from kitti car dataset
        frame_1 = Frame(1, self._load_image(
            os.path.join(self.base_path, 'data', 'kitti_car_1.png')), None)
        frame_2 = Frame(1, self._load_image(
            os.path.join(self.base_path, 'data', 'kitti_car_2.png')), None)

        # create a batch of 2 frames
        frame_batch = FrameBatch([frame_1, frame_2], None)

        # process the batch frames for depth and segmentation prediction
        estimator = DepthEstimator()
        result = estimator.process_frames(frame_batch)

        # assert if result size is same as the batch size
        self.assertEqual(len(result), 2)

        # assert if frame in result object is same as original frame
        self.assertTrue(np.array_equal(result[0].frame.data, frame_1.data))
        self.assertTrue(np.array_equal(result[1].frame.data, frame_2.data))

        # assert that depth and segmentation results should not be null
        assert result[0].depth is not None
        assert result[0].segm is not None
        assert result[1].depth is not None
        assert result[1].segm is not None
