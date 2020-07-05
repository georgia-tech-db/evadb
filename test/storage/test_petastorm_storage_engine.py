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
from src.storage.petastorm_storage_engine import PetastormStorageEngine
from src.storage.loaders.video_loader import VideoLoader
from test.util import custom_list_of_dicts_equal
from src.catalog.models.df_column import DataFrameColumn
from src.catalog.column_type import ColumnType

NUM_FRAMES = 10


class PetastormStorageEngineTest(unittest.TestCase):

    def create_dummy_frames(self, num_frames=NUM_FRAMES, filters=[]):
        if not filters:
            filters = range(num_frames)
        for i in filters:
            yield {'id': i,
                   'frame_data': np.array(np.ones((2, 2, 3)) * 0.1 * float(i + 1) * 255,
                                          dtype=np.uint8)}

    def create_sample_table(self):
        table_info = DataFrameMetadata("dataset_1", 'dummy.avi')
        column_1 = DataFrameColumn("id", ColumnType.INTEGER, False)
        column_2 = DataFrameColumn("frame_data", ColumnType.NDARRAY, False, [2, 2, 3])
        table_info.schema = [column_1, column_2]
        return table_info

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


    def test_should_create_empty_table(self):
        table_info = self.create_sample_table()
        petastorm = PetastormStorageEngine()
        petastorm.create(table_info)
        row_iter = petastorm.read(table_info)
        self.assertFalse(any(True for _ in row_iter))


    def test_should_return_equivalent_frames(self):
        table_info = self.create_sample_table()
        dummy_frames = list(self.create_dummy_frames())

        petastorm = PetastormStorageEngine()
        petastorm.create(table_info)
        petastorm.write_row(table_info, dummy_frames)

        expected_rows = list(petastorm.read(table_info))
        self.assertEqual(len(expected_rows), NUM_FRAMES)

        self.assertTrue(custom_list_of_dicts_equal(dummy_frames, expected_rows))

    def test_should_return_equivalent_frames_by_videoloader(self):
        """
        This is an integration test with videoloader.
        """
        table_info = self.create_sample_table()

        video_loader = VideoLoader(table_info)
        batches = list(video_loader.load())
        # Create a function to convert bacth to row
        # The Dict yielded from the videoloader should have the same schema
        # TODO: Type the Row object. Maybe?
        rows = [batch.frames.to_dict('records')[0] for batch in batches]

        petastorm = PetastormStorageEngine()
        petastorm.create(table_info)
        petastorm.write_row(table_info, rows)

        dummy_frames = list(self.create_dummy_frames())
        return_rows = list(petastorm.read(table_info))

        self.assertEqual(len(return_rows), NUM_FRAMES)
        self.assertTrue(custom_list_of_dicts_equal(dummy_frames, return_rows))
