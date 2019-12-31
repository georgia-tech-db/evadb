import os
import unittest

import cv2
import numpy as np

from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace, VideoFormat
from src.models.storage.frame import Frame

NUM_FRAMES = 10


class FrameLoaderTest(unittest.TestCase):

    def create_dummy_frames(self, num_frames=NUM_FRAMES, filters=[]):
        if not filters:
            filters = range(num_frames)
        for i in filters:
            yield Frame(i,
                        np.array(np.ones((2, 2, 3)) * 0.1 * float(i + 1) * 255,
                                 dtype=np.uint8),
                        FrameInfo(2, 2, 3, ColorSpace.BGR))

    def setUp(self):
        self.create_sample_video()

    def tearDown(self):
        os.remove('dummy.avi')
