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
import unittest
from unittest.mock import patch

import numpy as np

from src.catalog.models.df_metadata import DataFrameMetadata
from src.loaders.petastorm_loader import PetastormLoader
from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import VideoFormat, ColorSpace
from src.models.catalog.video_info import VideoMetaInfo
from src.models.storage.frame import Frame

NUM_FRAMES = 10


class PetastormLoaderTest(unittest.TestCase):
    class DummyRow:
        def __init__(self, frame_id, frame_data):
            self.frame_id = frame_id
            self.frame_data = frame_data

    class DummyReader:
        def __init__(self, data):
            self.data = data

        def __enter__(self):
            return self

        def __iter__(self):
            return self.data

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    @patch("src.loaders.petastorm_loader.make_reader")
    def test_should_call_petastorm_make_reader_with_correct_params(self,
                                                                   mock):
        video_info = DataFrameMetadata("dataset_1", 'dummy.avi')
        video_loader = PetastormLoader(video_info, shard=3, total_shards=3)
        list(video_loader._load_frames())
        mock.assert_called_once_with('dummy.avi', shard_count=3, cur_shard=3)

    @patch("src.loaders.petastorm_loader.make_reader")
    def test_load_frame_load_frames_using_petastorm(self, mock):
        mock.return_value = self.DummyReader(
            map(lambda i: self.DummyRow(i, np.ones((2, 2, 3)) * i), range(3)))

        video_info = DataFrameMetadata("dataset_1", 'dummy.avi')

        video_loader = PetastormLoader(video_info, shard=3, total_shards=3)
        actual = list(video_loader._load_frames())
        expected = [Frame(i, np.ones((2, 2, 3)) * i, FrameInfo(2, 2, 3,
                                                               ColorSpace.BGR))
                    for i in range(3)]

        self.assertEqual(expected, actual)
