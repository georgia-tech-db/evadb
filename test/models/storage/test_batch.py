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
import pandas as pd
import unittest

import numpy as np

from src.models.storage.batch import Batch
from test.util import create_dataframe_same, create_dataframe


class BatchTest(unittest.TestCase):

    def test_batch_from_json(self):
        batch = Batch(frames=create_dataframe(),
                      identifier_column='id')
        batch2 = Batch.from_json(batch.to_json())
        self.assertEqual(batch, batch2)

    def test_set_outcomes_method_should_set_the_predictions_with_udf_name(
            self):
        batch = Batch(frames=create_dataframe())
        batch.set_outcomes('test', [None])
        self.assertEqual([None], batch.get_outcomes_for('test'))

    def test_get_outcome_from_non_existing_udf_name_returns_empty_list(self):
        batch = Batch(frames=create_dataframe())
        self.assertEqual([], batch.get_outcomes_for('test'))

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

    def test_fetching_frames_by_index_should_also_return_outcomes(self):
        batch = Batch(
            frames=create_dataframe_same(2),
            outcomes={'test': [[None], [None]]})
        expected = Batch(frames=create_dataframe(),
                         outcomes={'test': [[None]]})
        self.assertEqual(expected, batch[[0]])

    def test_slicing_on_batched_should_return_new_batch_frame(self):
        batch = Batch(
            frames=create_dataframe(2),
            outcomes={'test': [[None], [None]]})
        expected = Batch(frames=create_dataframe(),
                         outcomes={'test': [[None]]})
        self.assertEqual(batch, batch[:])
        self.assertEqual(expected, batch[:-1])

    def test_slicing_should_word_for_negative_stop_value(self):
        batch = Batch(
            frames=create_dataframe(2),
            outcomes={'test': [[None], [None]]})
        expected = Batch(frames=create_dataframe(),
                         outcomes={'test': [[None]]})
        self.assertEqual(expected, batch[:-1])

    def test_slicing_should_work_with_skip_value(self):
        batch = Batch(
            frames=create_dataframe(3),
            outcomes={'test': [[None], [None], [None]]})
        expected = Batch(
            frames=create_dataframe(3).iloc[[0, 2], :],
            outcomes={'test': [[None], [None]]})
        self.assertEqual(expected, batch[::2])

    def test_fetching_frames_by_index_should_also_return_temp_outcomes(self):
        batch = Batch(
            frames=create_dataframe_same(2),
            outcomes={'test': [[1], [2]]},
            temp_outcomes={'test2': [[3], [4]]})
        expected = Batch(frames=create_dataframe(),
                         outcomes={'test': [[1]]},
                         temp_outcomes={'test2': [[3]]})
        self.assertEqual(expected, batch[[0]])

    def test_set_outcomes_method_should_set_temp_outcome_when_bool_is_true(
            self):
        batch = Batch(frames=create_dataframe())
        batch.set_outcomes('test', [1], is_temp=True)
        expected = Batch(frames=create_dataframe(),
                         temp_outcomes={'test': [1]})
        self.assertEqual(expected, batch)

    def test_has_outcomes_returns_false_if_the_given_name_not_in_outcomes(
            self):
        batch = Batch(frames=create_dataframe())

        self.assertFalse(batch.has_outcome('temp'))

    def test_has_outcomes_returns_true_if_the_given_name_is_in_outcomes(
            self):
        batch = Batch(frames=create_dataframe())
        batch.set_outcomes('test_temp', [1], is_temp=True)
        batch.set_outcomes('test', [1])

        self.assertTrue(batch.has_outcome('test'))
        self.assertTrue(batch.has_outcome('test_temp'))

    def test_add_should_raise_error_for_incompatible_type(self):
        batch = Batch(frames=create_dataframe())
        with self.assertRaises(TypeError):
            batch + 1

    def test_add_should_get_new_batch_frame_with_addition_no_outcomes(self):
        batch_1 = Batch(frames=create_dataframe())
        batch_2 = Batch(frames=create_dataframe())
        batch_3 = Batch(frames=create_dataframe_same(2))
        self.assertEqual(batch_3, batch_1 + batch_2)

    def test_adding_to_empty_frame_batch_returns_itself(self):
        batch_1 = Batch(frames=pd.DataFrame())
        batch_2 = Batch(frames=create_dataframe(), outcomes={'1': [1]})

        self.assertEqual(batch_2, batch_1 + batch_2)

    def test_adding_batch_frame_with_outcomes_returns_new_batch_frame(self):
        batch_1 = Batch(frames=create_dataframe(), outcomes={'1': [1]},
                        temp_outcomes={'2': [1]})
        batch_2 = Batch(frames=create_dataframe(), outcomes={'1': [2]},
                        temp_outcomes={'2': [2]})

        batch_3 = Batch(frames=create_dataframe_same(2),
                        outcomes={'1': [1, 2]},
                        temp_outcomes={'2': [1, 2]})

        self.assertEqual(batch_3, batch_1 + batch_2)

    def test_project_batch_frame(self):
        batch_1 = Batch(frames=pd.DataFrame([{'id': 1,
                                              'data': 2,
                                              'info': 3}]))
        batch_2 = batch_1.project(['id', 'info'])
        batch_3 = Batch(frames=pd.DataFrame([{'id': 1,
                                              'info': 3}]))
        self.assertEqual(batch_2, batch_3)

    def test_merge_column_wise_batch_frame(self):
        batch_1 = Batch(frames=pd.DataFrame([{'id': 0}]))
        batch_2 = Batch(frames=pd.DataFrame([{'data': 1}]))

        batch_3 = Batch.merge_column_wise([batch_1, batch_2])
        batch_4 = Batch(frames=pd.DataFrame([{'id': 0, 'data': 1}]))
        self.assertEqual(batch_3, batch_4)

    def test_should_fail_for_list(self):
        frames = [{'id': 0, 'data': [1, 2]}, {'id': 1, 'data': [1, 2]}]
        self.assertRaises(ValueError, Batch, frames)

    def test_should_fail_for_dict(self):
        frames = {'id': 0, 'data': [1, 2]}
        self.assertRaises(ValueError, Batch, frames)

    def test_should_return_correct_length(self):
        batch = Batch(create_dataframe(5))
        self.assertEqual(5, len(batch))

    def test_should_return_empty_dataframe(self):
        batch = Batch()
        self.assertEqual(batch, Batch(create_dataframe(0)))
