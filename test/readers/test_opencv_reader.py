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
from unittest.mock import patch

from src.readers.opencv_reader import OpenCVReader

from test.util import create_sample_video
from test.util import create_dummy_batches
from test.util import file_remove
from test.util import NUM_FRAMES, PATH_PREFIX


class VideoLoaderTest(unittest.TestCase):

    def setUp(self):
        create_sample_video()

    def tearDown(self):
        file_remove('dummy.avi')

    def test_should_return_one_batch(self):
        video_loader = OpenCVReader(
            file_url=os.path.join(PATH_PREFIX, 'dummy.avi'))
        batches = list(video_loader.read())
        expected = list(create_dummy_batches())
        self.assertTrue(batches, expected)

    def test_should_return_batches_equivalent_to_number_of_frames(self):
        video_loader = OpenCVReader(
            file_url=os.path.join(PATH_PREFIX, 'dummy.avi'),
            batch_mem_size=1)
        batches = list(video_loader.read())
        expected = list(create_dummy_batches(batch_size=1))
        self.assertTrue(batches, expected)

    def test_should_return_one_batches_for_negative_size(self):
        video_loader = OpenCVReader(
            file_url=os.path.join(PATH_PREFIX, 'dummy.avi'),
            batch_mem_size=-1)
        batches = list(video_loader.read())
        expected = list(create_dummy_batches())
        self.assertTrue(batches, expected)

    def test_should_skip_first_two_frames_with_offset_two(self):
        video_loader = OpenCVReader(
            file_url=os.path.join(PATH_PREFIX, 'dummy.avi'),
            offset=2)
        batches = list(video_loader.read())
        expected = list(create_dummy_batches(
            filters=[i for i in range(2, NUM_FRAMES)]))

        self.assertTrue(batches, expected)

    def test_should_skip_first_two_frames_and_batch_size_equal_to_no_of_frames(
            self):
        video_loader = OpenCVReader(
            file_url=os.path.join(PATH_PREFIX, 'dummy.avi'),
            batch_mem_size=NUM_FRAMES,
            offset=2)
        batches = list(video_loader.read())
        expected = list(create_dummy_batches(
            filters=[i for i in range(2, NUM_FRAMES)]))
        self.assertTrue(batches, expected)

    def test_should_start_frame_number_from_two(self):
        video_loader = OpenCVReader(
            file_url=os.path.join(PATH_PREFIX, 'dummy.avi'),
            batch_mem_size=NUM_FRAMES,
            start_frame_id=2)
        batches = list(video_loader.read())
        expected = list(create_dummy_batches(
            filters=[i for i in range(0, NUM_FRAMES)], start_id=2))
        self.assertTrue(batches, expected)

    def test_should_start_frame_number_from_two_and_offset_from_one(self):
        video_loader = OpenCVReader(
            file_url=os.path.join(PATH_PREFIX, 'dummy.avi'),
            batch_mem_size=NUM_FRAMES,
            offset=1,
            start_frame_id=2)
        batches = list(video_loader.read())
        expected = list(create_dummy_batches(
            filters=[i for i in range(1, NUM_FRAMES)], start_id=2))
        self.assertTrue(batches, expected)

    @patch('src.readers.abstract_reader.ConfigurationManager.get_value')
    def test_should_work_if_batch_mem_size_not_in_config(self, get_val_mock):
        get_val_mock.return_value = None
        video_loader = OpenCVReader(
            file_url=os.path.join(PATH_PREFIX, 'dummy.avi'))
        batches = list(video_loader.read())
        expected = list(create_dummy_batches())
        self.assertTrue(batches, expected)
        get_val_mock.assert_called_once_with("executor", "batch_mem_size")
