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
import os
import unittest

import cv2
import numpy as np

from src.catalog.models.df_metadata import DataFrameMetadata
from src.loaders.video_loader import VideoLoader
from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace
from src.models.storage.frame import Frame

NUM_FRAMES = 10


class VideoLoaderTest(unittest.TestCase):

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

    def setUp(self):
        self.create_sample_video()

    def tearDown(self):
        os.remove('dummy.avi')

    def test_should_return_batches_equivalent_to_number_of_frames(self):
        video_info = DataFrameMetadata("dataset_1", 'dummy.avi')
        video_loader = VideoLoader(video_info)
        batches = list(video_loader.load())
        dummy_frames = list(self.create_dummy_frames())
        self.assertEqual(len(batches), NUM_FRAMES)
        self.assertEqual(dummy_frames, [batch.frames[0] for batch in batches])

    def test_should_return_half_then_number_of_batches_with_skip_of_two(self):
        video_info = DataFrameMetadata("dataset_1", 'dummy.avi')
        video_loader = VideoLoader(video_info, skip_frames=2)
        batches = list(video_loader.load())
        dummy_frames = list(
            self.create_dummy_frames(
                filters=[i * 2 for i in range(NUM_FRAMES // 2)]))
        self.assertEqual(len(batches), NUM_FRAMES / 2)
        self.assertEqual(dummy_frames, [batch.frames[0] for batch in batches])

    def test_should_skip_first_two_frames_with_offset_two(self):
        video_info = DataFrameMetadata("dataset_1", 'dummy.avi')
        video_loader = VideoLoader(video_info, offset=2)
        dummy_frames = list(
            self.create_dummy_frames(
                filters=[i for i in range(2, NUM_FRAMES)]))
        batches = list(video_loader.load())
        self.assertEqual(NUM_FRAMES - 2, len(batches))
        self.assertEqual(dummy_frames, [batch.frames[0] for batch in batches])

    def test_should_return_only_few_frames_when_limit_is_specified(self):
        video_info = DataFrameMetadata("dataset_1", 'dummy.avi')
        limit = 4
        video_loader = VideoLoader(video_info, limit=limit)
        dummy_frames = list(
            self.create_dummy_frames(filters=[i for i in range(limit)]))
        batches = list(video_loader.load())
        self.assertEqual(limit, len(batches))
        self.assertEqual(dummy_frames, [batch.frames[0] for batch in batches])

    def test_should_return_single_batch_if_batch_size_equal_to_no_of_frames(
            self):
        video_info = DataFrameMetadata("dataset_1", 'dummy.avi')
        video_loader = VideoLoader(video_info, batch_size=NUM_FRAMES)
        dummy_frames = list(
            self.create_dummy_frames(filters=[i for i in range(NUM_FRAMES)]))
        batches = list(video_loader.load())
        self.assertEqual(1, len(batches))
        self.assertEqual(dummy_frames, list(batches[0].frames))
