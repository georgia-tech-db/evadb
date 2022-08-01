# coding=utf-8
# Copyright 2018-2022 EVA
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
from test.util import (
    FRAME_SIZE,
    NUM_FRAMES,
    PATH_PREFIX,
    create_dummy_batches,
    create_sample_video,
    file_remove,
)

from eva.readers.opencv_reader import OpenCVReader


class VideoLoaderTest(unittest.TestCase):
    def setUp(self):
        create_sample_video()

    def tearDown(self):
        file_remove("dummy.avi")

    def test_should_return_one_batch(self):
        video_loader = OpenCVReader(
            file_url=os.path.join(PATH_PREFIX, "dummy.avi"),
            batch_mem_size=NUM_FRAMES * FRAME_SIZE,
        )
        batches = list(video_loader.read())
        expected = list(create_dummy_batches())
        self.assertTrue(batches, expected)

    def test_should_return_batches_equivalent_to_number_of_frames(self):
        video_loader = OpenCVReader(
            file_url=os.path.join(PATH_PREFIX, "dummy.avi"), batch_mem_size=FRAME_SIZE
        )
        batches = list(video_loader.read())
        expected = list(create_dummy_batches(batch_size=1))
        self.assertTrue(batches, expected)

    def test_should_skip_first_two_frames_with_offset_two(self):
        video_loader = OpenCVReader(
            file_url=os.path.join(PATH_PREFIX, "dummy.avi"),
            batch_mem_size=FRAME_SIZE * (NUM_FRAMES - 2),
            offset=2,
        )
        batches = list(video_loader.read())
        expected = list(create_dummy_batches(filters=[i for i in range(2, NUM_FRAMES)]))

        self.assertTrue(batches, expected)

    def test_should_skip_first_two_frames_and_batch_size_equal_to_no_of_frames(self):
        video_loader = OpenCVReader(
            file_url=os.path.join(PATH_PREFIX, "dummy.avi"),
            batch_mem_size=FRAME_SIZE * NUM_FRAMES,
            offset=2,
        )
        batches = list(video_loader.read())
        expected = list(create_dummy_batches(filters=[i for i in range(2, NUM_FRAMES)]))
        self.assertTrue(batches, expected)
