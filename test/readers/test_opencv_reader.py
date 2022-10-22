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
    create_dummy_batches,
    create_sample_video,
    file_remove,
    upload_dir_from_config,
)

from eva.expression.abstract_expression import ExpressionType
from eva.expression.comparison_expression import ComparisonExpression
from eva.expression.constant_value_expression import ConstantValueExpression
from eva.expression.logical_expression import LogicalExpression
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.readers.opencv_reader import OpenCVReader


class VideoLoaderTest(unittest.TestCase):
    def setUp(self):
        create_sample_video()

    def tearDown(self):
        file_remove("dummy.avi")

    def test_should_return_one_batch(self):
        video_loader = OpenCVReader(
            file_url=os.path.join(upload_dir_from_config, "dummy.avi"),
            batch_mem_size=NUM_FRAMES * FRAME_SIZE,
        )
        batches = list(video_loader.read())
        expected = list(create_dummy_batches())
        self.assertTrue(batches, expected)

    def test_should_return_batches_equivalent_to_number_of_frames(self):
        video_loader = OpenCVReader(
            file_url=os.path.join(upload_dir_from_config, "dummy.avi"),
            batch_mem_size=FRAME_SIZE,
        )
        batches = list(video_loader.read())
        expected = list(create_dummy_batches(batch_size=1))
        self.assertTrue(batches, expected)

    def test_should_skip_first_two_frames_with_offset_two(self):
        video_loader = OpenCVReader(
            file_url=os.path.join(upload_dir_from_config, "dummy.avi"),
            batch_mem_size=FRAME_SIZE * (NUM_FRAMES - 2),
            offset=2,
        )
        batches = list(video_loader.read())
        expected = list(create_dummy_batches(filters=[i for i in range(2, NUM_FRAMES)]))

        self.assertTrue(batches, expected)

    def test_should_start_frame_number_from_two(self):
        video_loader = OpenCVReader(
            file_url=os.path.join(upload_dir_from_config, "dummy.avi"),
            batch_mem_size=FRAME_SIZE * NUM_FRAMES,
            offset=2,
        )
        batches = list(video_loader.read())
        expected = list(
            create_dummy_batches(filters=[i for i in range(0, NUM_FRAMES)], start_id=2)
        )
        self.assertTrue(batches, expected)

    def test_should_skip_first_two_frames_and_batch_size_equal_to_no_of_frames(
        self,
    ):
        video_loader = OpenCVReader(
            file_url=os.path.join(upload_dir_from_config, "dummy.avi"),
            batch_mem_size=FRAME_SIZE * NUM_FRAMES,
            offset=2,
        )
        batches = list(video_loader.read())
        expected = list(create_dummy_batches(filters=[i for i in range(2, NUM_FRAMES)]))
        self.assertTrue(batches, expected)

    def test_should_sample_every_k_frame(self):
        for k in range(1, 10):
            video_loader = OpenCVReader(
                file_url=os.path.join(upload_dir_from_config, "dummy.avi"),
                batch_mem_size=FRAME_SIZE * NUM_FRAMES,
                sampling_rate=k,
            )
            batches = list(video_loader.read())
            expected = list(
                create_dummy_batches(filters=[i for i in range(0, NUM_FRAMES, k)])
            )
            self.assertTrue(batches, expected)

    def test_should_sample_every_k_frame_with_predicate(self):
        col = TupleValueExpression("id")
        val = ConstantValueExpression(NUM_FRAMES // 2)
        predicate = ComparisonExpression(
            ExpressionType.COMPARE_GEQ, left=col, right=val
        )
        for k in range(2, 4):
            video_loader = OpenCVReader(
                file_url=os.path.join(upload_dir_from_config, "dummy.avi"),
                batch_mem_size=FRAME_SIZE * NUM_FRAMES,
                sampling_rate=k,
                predicate=predicate,
            )
            batches = list(video_loader.read())
            for batch in batches:
                print(batch)
            value = NUM_FRAMES // 2
            start = value + k - (value % k) if value % k else value
            expected = list(
                create_dummy_batches(filters=[i for i in range(start, NUM_FRAMES, k)])
            )
        self.assertTrue(batches, expected)

        value = 2
        predicate_1 = ComparisonExpression(
            ExpressionType.COMPARE_GEQ,
            left=TupleValueExpression("id"),
            right=ConstantValueExpression(value),
        )
        predicate_2 = ComparisonExpression(
            ExpressionType.COMPARE_LEQ,
            left=TupleValueExpression("id"),
            right=ConstantValueExpression(8),
        )
        predicate = LogicalExpression(
            ExpressionType.LOGICAL_AND, predicate_1, predicate_2
        )
        for k in range(2, 4):
            video_loader = OpenCVReader(
                file_url=os.path.join(upload_dir_from_config, "dummy.avi"),
                batch_mem_size=FRAME_SIZE * NUM_FRAMES,
                sampling_rate=k,
                predicate=predicate,
            )
            batches = list(video_loader.read())
            start = value + k - (value % k) if value % k else value
            expected = list(
                create_dummy_batches(filters=[i for i in range(start, 8, k)])
            )
        self.assertTrue(batches, expected)
