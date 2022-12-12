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
import unittest
from test.util import create_dataframe, create_dataframe_same

import numpy as np
import pandas as pd

from eva.models.storage.batch import Batch


class BatchTest(unittest.TestCase):
    def test_batch_serialize_deserialize(self):
        batch = Batch(frames=create_dataframe())
        batch2 = Batch.deserialize(batch.serialize())
        self.assertEqual(batch, batch2)

    def test_frames_as_numpy_array_should_frames_as_numpy_array(self):
        batch = Batch(frames=create_dataframe_same(2))
        expected = list(np.ones((2, 1, 1)))
        actual = list(batch.column_as_numpy_array())
        self.assertEqual(expected, actual)

    def test_return_only_frames_specified_in_the_indices(self):
        batch = Batch(frames=create_dataframe(2))
        expected = Batch(frames=create_dataframe())
        output = batch[[0]]
        self.assertEqual(expected, output)

    def test_fetching_frames_by_index(self):
        batch = Batch(frames=create_dataframe_same(2))
        expected = Batch(frames=create_dataframe())
        self.assertEqual(expected, batch[0])

    def test_fetching_frames_by_index_should_raise(self):
        batch = Batch(frames=create_dataframe_same(2))
        with self.assertRaises(TypeError):
            batch[1.0]

    def test_slicing_on_batched_should_return_new_batch_frame(self):
        batch = Batch(frames=create_dataframe(2))
        expected = Batch(frames=create_dataframe())
        self.assertEqual(batch, batch[:])
        self.assertEqual(expected, batch[:-1])

    def test_slicing_should_word_for_negative_stop_value(self):
        batch = Batch(frames=create_dataframe(2))
        expected = Batch(frames=create_dataframe())
        self.assertEqual(expected, batch[:-1])

    def test_slicing_should_work_with_skip_value(self):
        batch = Batch(frames=create_dataframe(3))
        expected = Batch(frames=create_dataframe(3).iloc[[0, 2], :])
        self.assertEqual(expected, batch[::2])

    def test_add_should_raise_error_for_incompatible_type(self):
        batch = Batch(frames=create_dataframe())
        with self.assertRaises(TypeError):
            batch + 1

    def test_adding_to_empty_frame_batch_returns_itself(self):
        batch_1 = Batch(frames=pd.DataFrame())
        batch_2 = Batch(frames=create_dataframe())

        self.assertEqual(batch_2, batch_1 + batch_2)

    def test_adding_batch_frame_with_outcomes_returns_new_batch_frame(self):
        batch_1 = Batch(frames=create_dataframe())
        batch_2 = Batch(frames=create_dataframe())

        batch_3 = Batch(frames=create_dataframe_same(2))

        self.assertEqual(batch_3, batch_1 + batch_2)

    def test_concat_batch(self):
        batch_1 = Batch(frames=create_dataframe())
        batch_2 = Batch(frames=create_dataframe())
        batch_3 = Batch(frames=create_dataframe_same(2))
        self.assertEqual(batch_3, Batch.concat([batch_1, batch_2], copy=False))

    def test_concat_empty_batch_list_raise_exception(self):
        self.assertEqual(Batch(), Batch.concat([]))

    def test_project_batch_frame(self):
        batch_1 = Batch(frames=pd.DataFrame([{"id": 1, "data": 2, "info": 3}]))
        batch_2 = batch_1.project(["id", "info"])
        batch_3 = Batch(frames=pd.DataFrame([{"id": 1, "info": 3}]))
        self.assertEqual(batch_2, batch_3)

    def test_merge_column_wise_batch_frame(self):
        batch_1 = Batch(frames=pd.DataFrame([{"id": 0}]))
        batch_2 = Batch(frames=pd.DataFrame([{"data": 1}]))

        batch_3 = Batch.merge_column_wise([batch_1, batch_2])
        batch_4 = Batch(frames=pd.DataFrame([{"id": 0, "data": 1}]))
        self.assertEqual(batch_3, batch_4)

    def test_should_fail_for_list(self):
        frames = [{"id": 0, "data": [1, 2]}, {"id": 1, "data": [1, 2]}]
        self.assertRaises(ValueError, Batch, frames)

    def test_should_fail_for_dict(self):
        frames = {"id": 0, "data": [1, 2]}
        self.assertRaises(ValueError, Batch, frames)

    def test_should_return_correct_length(self):
        batch = Batch(create_dataframe(5))
        self.assertEqual(5, len(batch))

    def test_should_return_empty_dataframe(self):
        batch = Batch()
        self.assertEqual(batch, Batch(create_dataframe(0)))

    def test_stack_batch_more_than_one_column_should_raise_exception(self):
        batch = Batch(create_dataframe_same(2))
        self.assertRaises(ValueError, Batch.stack, batch)
        # TODO ACTION: Add test cases for stack correctness
