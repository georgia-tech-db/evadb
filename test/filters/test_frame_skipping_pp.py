import unittest

import cv2
import numpy as np

from src.models.storage.frame import Frame
from src.models.catalog.frame_info import FrameInfo
from src.models.storage.batch import FrameBatch
from src.models.catalog.properties import ColorSpace
from src.filters.frame_skipping_pp import FrameSkippingPP, DistanceMetric as DM


class FrameSkippingPPTest(unittest.TestCase):
    def create_batch_with_similar_frames(self):
        """
        Function to create a batch with 2 identical frames. 
        Useful for testing frame differencing.

        :param: None
        :return batch: EVA FrameBatch of 2 frames        
        """

        frame = np.array(np.ones((2, 2, 3)) * 0.1 * 255,
                         dtype=np.uint8)
        (height, width, channels) = frame.shape
        info = FrameInfo(height, width, channels, ColorSpace.BGR)
        frames = []

        """
        Creating identical frames
        """
        eva_frame1 = Frame(1, frame, info)
        eva_frame2 = Frame(1, frame, info)
        frames.append(eva_frame1)
        frames.append(eva_frame2)
        batch = FrameBatch(frames, info)

        return batch

    def create_batch_with_similar_frames_contours(self):
        """
        Function to create a batch with 2 identical frames with contours. 
        Useful for testing frame differencing by conparing foregound objects.

        :param: None
        :return batch: EVA FrameBatch of 2 frames
        """

        frame = np.array(np.ones((2000, 2000, 3)) * 80,
                         dtype=np.uint8)
        frame = cv2.circle(frame, (1010, 1000), 150, (36, 36, 36), 2)

        (height, width, channels) = frame.shape
        info = FrameInfo(height, width, channels, ColorSpace.BGR)
        frames = []

        """
        Creating identical frames with contours
        """
        eva_frame1 = Frame(1, frame, info)
        eva_frame2 = Frame(1, frame, info)
        frames.append(eva_frame1)
        frames.append(eva_frame2)
        batch = FrameBatch(frames, info)

        return batch

    def test_should_skip_identical_frames_absdiff(self):
        """
        -> Test to create a batch of two identical frames and skip 
            identical ones.
        -> Test compares all the pixels in the two frames using
            distance metric as absolute difference.
        -> Test should return a list of two booleans with the first value
        set to False and the second set to True. This implies only second
        frame is skipped since it is the same as the first one.

        :param: None
        :return: None
        """
        batch = self.create_batch_with_similar_frames()
        frame_skipping_pp = FrameSkippingPP(0.5, False, 
                                            DM.ABSOLUTE_DIFFERENCE.value)
        skip_list = frame_skipping_pp.predict(batch)
        self.assertEqual(2, len(skip_list))
        self.assertEqual(False, skip_list[0])
        self.assertEqual(True, skip_list[1])

    def test_should_skip_identical_frames_msediff(self):
        """
        -> Test to create a batch of two identical frames and skip 
            identical ones.
        -> Test compares all the pixels in the two frames using
            distance metric as mean squared error.
        -> Test should return a list of two booleans with the first value
        set to False and the second set to True. This implies only second
        frame is skipped since it is the same as the first one.

        :param: None
        :return: None
        """
        batch = self.create_batch_with_similar_frames()
        frame_skipping_pp = FrameSkippingPP(0.5, False, 
                                            DM.MSE_DIFFERENCE.value)
        skip_list = frame_skipping_pp.predict(batch)
        self.assertEqual(2, len(skip_list))
        self.assertEqual(False, skip_list[0])
        self.assertEqual(True, skip_list[1])

    def test_should_skip_identical_frames_only_foreground_abs(self):
        """
        -> Test to create a batch of two identical frames with contours 
            and skip identical ones.
        -> Test compares only foreground objects in the two frames using
        distance metric as absolute difference.
        -> Test should return a list of two booleans with the first value
        set to False and the second set to True. This implies only second
        frame is skipped since it is the same as the first one.

        :param: None
        :return: None
        """
        batch = self.create_batch_with_similar_frames()
        frame_skipping_pp = FrameSkippingPP(0.5, False, 
                                            DM.ABSOLUTE_DIFFERENCE.value)
        skip_list = frame_skipping_pp.predict(batch)
        self.assertEqual(2, len(skip_list))
        self.assertEqual(False, skip_list[0])
        self.assertEqual(True, skip_list[1])

    def test_should_skip_identical_frames_only_foreground_abs(self):
        """
        -> Test to create a batch of two identical frames with contours 
            and skip identical ones.
        -> Test compares only foreground objects in the two frames using
        distance metric as absolute difference.
        -> Test should return a list of two booleans with the first value
        set to False and the second set to True. This implies only second
        frame is skipped since it is the same as the first one.

        :param: None
        :return: None
        """
        batch = self.create_batch_with_similar_frames()
        frame_skipping_pp = FrameSkippingPP(0.5, False, 
                                            DM.MSE_DIFFERENCE.value)
        skip_list = frame_skipping_pp.predict(batch)
        self.assertEqual(2, len(skip_list))
        self.assertEqual(False, skip_list[0])
        self.assertEqual(True, skip_list[1])
