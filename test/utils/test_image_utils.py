import unittest
import cv2
import numpy as np
from src.utils import image_utils


class ImageUtilsTest(unittest.TestCase):
    def test_should_convert_image_to_grayscale(self):
        """
        -> Test grayscale image conversion reduces number
        of channels from 3 to 1

        :param: None
        :return: None
        """

        frame = np.array(np.ones((2, 2, 3)) * 0.1 * 255,
                         dtype=np.uint8)
        grayscale = image_utils.convert_to_grayscale(frame)
        self.assertEqual(3, len(frame.shape))
        self.assertEqual(2, len(grayscale.shape))

    def test_should_return_absolute_difference(self):
        """
        -> Test absolute difference between two frames.
        Test should return 0 when the same frames are passed.

        :param: None
        :return: None
        """

        frame = np.array(np.ones((2, 2, 3)) * 0.1 * 255,
                         dtype=np.uint8)
        diff = image_utils.absolute_difference(frame, frame)
        self.assertEqual(0, diff)

    def test_should_return_mse_difference(self):
        """
        -> Test mean squared difference between two frames.
        Test should return 0 when the same frames are passed.

        :param: None
        :return: None
        """

        frame = np.array(np.ones((2, 2, 3)) * 0.1 * 255,
                         dtype=np.uint8)
        diff = image_utils.mse_difference(frame, frame)
        self.assertEqual(0, diff)

    def test_should_return_masked_image(self):
        """
        -> Test should return an image with background masked.
        Masked image should same or greater 0s that original.

        :param: None
        :return: None
        """

        frame = np.array(np.ones((2000, 2000, 3)) * 80,
                         dtype=np.uint8)
        frame = cv2.circle(frame, (1010, 1000), 150, (36, 36, 36), 2)
        masked_frame = image_utils.mask_background(frame)
        masked_frame_zeros = np.count_nonzero(masked_frame == 0)
        frame_zeros = np.count_nonzero(frame == 0)
        self.assertGreaterEqual(masked_frame_zeros, frame_zeros)
