import os
import unittest

import cv2
import numpy as np

from src.loaders.video_loader import SimpleVideoLoader
from src.models import VideoMetaInfo, VideoFormat, Frame, ColorSpace, FrameInfo
import glob
from src.utils import framediff_utils

NUM_FRAMES = 10


class SimpleVideoLoaderTest(unittest.TestCase):

    def create_dummy_frames(self, num_frames=NUM_FRAMES, filters=[]):
        if not filters:
            filters = range(num_frames)
        for i in filters:
            yield Frame(i,
                        np.array(np.ones((2, 2, 3)) * 0.1 * float(i + 1) * 255,
                                 dtype=np.uint8),
                        FrameInfo(2, 2, 3, ColorSpace.BGR))

    def create_sample_video(self):
        try:
            os.remove('dummy.avi')
        except FileNotFoundError:
            pass

        out = cv2.VideoWriter('dummy.avi',
                              cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10,
                              (2, 2))
        for i in range(NUM_FRAMES):
            frame = np.array(np.ones((2, 2, 3)) * 0.1 * float(i + 1) * 255,
                             dtype=np.uint8)
            out.write(frame)

    def create_sample_video_with_contours(self):
        """
        Function to create a video with 2 identical frames with a circle.
        Circle is used by the compare_foreground_mask of framediff_utils 
        module to identify background and mask it.
        Useful for testing frame differencing.
        """
        try:
            os.remove('dummy_contours.avi')
        except FileNotFoundError:
            pass

        out = cv2.VideoWriter('dummy_contours.avi',
                              cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10,
                              (2000, 2000))
        frame = np.array(np.ones((2000, 2000, 3)) * 80,
                         dtype=np.uint8)
        frame = cv2.circle(frame, (1010, 1000), 150, (36, 36, 36), 2)

        # Writing identical frames
        out.write(frame)
        out.write(frame)       

    def create_sample_video_with_similar_frames(self):
        """
        Function to create a video with 2 identical frames. 
        Useful for testing frame differencing.
        """
        try:
            os.remove('dummy_similar.avi')
        except FileNotFoundError:
            pass

        out = cv2.VideoWriter('dummy_similar.avi',
                              cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10,
                              (2, 2))
        frame = np.array(np.ones((2, 2, 3)) * 0.1 * 255,
                         dtype=np.uint8)

        # Writing identical frames
        out.write(frame)
        out.write(frame)

    def setUp(self):
        self.create_sample_video()
        self.create_sample_video_with_similar_frames()
        self.create_sample_video_with_contours()

    def tearDown(self):
        os.remove('dummy.avi')
        os.remove('dummy_similar.avi')
        os.remove('dummy_contours.avi')

    def test_should_return_batches_equivalent_to_number_of_frames(self):
        video_info = VideoMetaInfo('dummy.avi', 10, VideoFormat.MPEG)
        video_loader = SimpleVideoLoader(video_info)
        batches = list(video_loader.load())
        dummy_frames = list(self.create_dummy_frames())
        self.assertEqual(len(batches), NUM_FRAMES)
        self.assertEqual(dummy_frames, [batch.frames[0] for batch in batches])

    def test_should_return_half_then_number_of_batches_with_skip_of_two(self):
        video_info = VideoMetaInfo('dummy.avi', 10, VideoFormat.MPEG)
        video_loader = SimpleVideoLoader(video_info, skip_frames=2)
        batches = list(video_loader.load())
        dummy_frames = list(
            self.create_dummy_frames(
                filters=[i * 2 for i in range(NUM_FRAMES // 2)]))
        self.assertEqual(len(batches), NUM_FRAMES / 2)
        self.assertEqual(dummy_frames, [batch.frames[0] for batch in batches])

    def test_should_skip_first_two_frames_with_offset_two(self):
        video_info = VideoMetaInfo('dummy.avi', 10, VideoFormat.MPEG)
        video_loader = SimpleVideoLoader(video_info, offset=2)
        dummy_frames = list(
            self.create_dummy_frames(
                filters=[i for i in range(2, NUM_FRAMES)]))
        batches = list(video_loader.load())
        self.assertEqual(NUM_FRAMES - 2, len(batches))
        self.assertEqual(dummy_frames, [batch.frames[0] for batch in batches])

    def test_should_return_only_few_frames_when_limit_is_specified(self):
        video_info = VideoMetaInfo('dummy.avi', 10, VideoFormat.MPEG)
        limit = 4
        video_loader = SimpleVideoLoader(video_info, limit=limit)
        dummy_frames = list(
            self.create_dummy_frames(filters=[i for i in range(limit)]))
        batches = list(video_loader.load())
        self.assertEqual(limit, len(batches))
        self.assertEqual(dummy_frames, [batch.frames[0] for batch in batches])

    def test_should_return_single_batch_if_batch_size_equal_to_no_of_frames(
            self):
        video_info = VideoMetaInfo('dummy.avi', 10, VideoFormat.MPEG)
        video_loader = SimpleVideoLoader(video_info, batch_size=NUM_FRAMES)
        dummy_frames = list(
            self.create_dummy_frames(filters=[i for i in range(NUM_FRAMES)]))
        batches = list(video_loader.load())
        self.assertEqual(1, len(batches))
        self.assertEqual(dummy_frames, list(batches[0].frames))

    def test_should_skip_identical_frames(self):
        video_info = VideoMetaInfo('dummy_similar.avi', 10, VideoFormat.MPEG)
        video_loader = SimpleVideoLoader(
            video_info, threshold=0.5, distance_metric='absolute_difference')
        batches = list(video_loader.load())
        self.assertEqual(1, len(batches))

    def test_should_skip_identical_frames_only_foreground(self):
        video_info = VideoMetaInfo('dummy_contours.avi', 10, VideoFormat.MPEG)
        video_loader = SimpleVideoLoader(
            video_info, threshold=0.5, distance_metric='absolute_difference',
            compare_foreground=True)
        batches = list(video_loader.load())
        self.assertEqual(1, len(batches))

