import os
import unittest
import cv2
import sys
import numpy as np

from src.models.storage.frame import Frame
from src.models.storage.batch import FrameBatch
from src.udfs.depth_estimation.depth_estimator import DepthEstimator
from src.utils.frame_filter_util import FrameFilter


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
                Unit test method which creates a batch of frames, sends it for
                model prediction.
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
        estimator = DepthEstimator('ExpKITTI_joint.ckpt')
        result = estimator.classify(frame_batch)

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

    @unittest.skip("need correction in depth mask initialization")
    def test_frame_filtering_for_depth_estimation(self):
        """
            Unit test method to test frame filtering functionality.
            it loops over frames and sends them over to frame filtering
            object's apply_filter method.
            Finally it verifies that depth mask is applied to the frames
            except every fifth one.

        """

        # create two frames from kitti car dataset
        frame_1 = Frame(1, self._load_image(
            os.path.join(self.base_path, 'data', 'kitti_car_1.png')), None)
        frame_2 = Frame(1, self._load_image(
            os.path.join(self.base_path, 'data', 'kitti_car_2.png')), None)

        # create a batch of 2 frames
        frame_batch = FrameBatch([frame_1, frame_2], None)

        frames = frame_batch.frames_as_numpy_array()

        # initialize the frame filtering class object
        frame_filter = FrameFilter()

        # create a random depth mask array
        depth_mask = np.random.rand(
            frames[0].shape[0],
            frames[0].shape[1],
            frames[0].shape[2])

        # iterate over frames in the batch
        for i, img in enumerate(frames):

            # apply frame filter on each frame
            img = frame_filter.apply_filter(img, depth_mask)

            # For every fifth frame the mask should not be applied. Hence, the
            # frame returned by apply_filter method should be same as original
            # frame
            if i % 5 == 0:
                self.assertTrue(np.array_equal(img, frames[0]))
            else:
                # Every other frame should be transformed after applying depth
                # mask
                self.assertTrue(np.array_equal(
                    img, frames[i] * depth_mask[:, :, None]))
