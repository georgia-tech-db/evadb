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

	def test_absolute_distance_metric(self):
		"""
        -> Test absolute difference between two frames.
        Test should return 0 when the same frames are passed.

        :param: None
        :return: None
        """

		frame = np.array(np.ones((2, 2, 3)) * 0.1 * 255,
                         dtype=np.uint8)
		diff = image_utils.absolute_difference(frame, frame)
		print(diff)
		self.assertEqual(0, diff)
