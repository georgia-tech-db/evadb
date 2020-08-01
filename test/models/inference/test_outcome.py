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

from src.models.inference.outcome import Outcome


class OutcomeTest(unittest.TestCase):
    def test_get_attribute_should_return_new_outcome(self):
        data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        outcome = Outcome(data, identifier='A')
        expected = Outcome(data[["A"]], identifier='A')
        self.assertEqual(outcome.A, expected)

    def test_equals_should_return_true_if_alreast_one_value_equal(self):
        data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        outcome = Outcome(data, identifier='A')
        self.assertTrue(getattr(outcome, 'A') == 1)

    def test_equals_should_return_false_frame_if_no_value_in_data_frame_equal(
            self):
        data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        outcome = Outcome(data, identifier='A')
        self.assertFalse(outcome.A == 4)

    def test_gt_should_return_false_if_no_value_gt_given(
            self):
        data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        outcome = Outcome(data, identifier='A')
        self.assertFalse(outcome.A > 4)

    def test_gt_should_return_true_if_atleast_one_value_gt_given(
            self):
        data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        outcome = Outcome(data, identifier='A')
        self.assertTrue(outcome.A > 2)

    def test_gte_should_return_false_if_no_value_gte_given(
            self):
        data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        outcome = Outcome(data, identifier='A')
        self.assertFalse(outcome.A >= 4)

    def test_gte_should_return_true_if_atleast_one_value_gte_given(
            self):
        data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        outcome = Outcome(data, identifier='A')
        self.assertTrue(outcome.A >= 3)

    def test_lt_should_return_false_if_no_value_lt_given(
            self):
        data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        outcome = Outcome(data, identifier='A')
        self.assertFalse(outcome.A < 0)

    def test_lt_should_return_true_if_atleast_one_value_lt_given(
            self):
        data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        outcome = Outcome(data, identifier='A')
        self.assertTrue(outcome.A < 4)

    def test_lte_should_return_false_if_no_value_lte_given(
            self):
        data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        outcome = Outcome(data, identifier='A')
        self.assertFalse(outcome.A < 1)

    def test_lte_should_return_true_if_atleast_one_value_lte_given(
            self):
        data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        outcome = Outcome(data, identifier='A')
        self.assertTrue(outcome.A <= 3)

    def test_ne_should_return_false_if_value_present_atleast_once(
            self):
        data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        outcome = Outcome(data, identifier='A')
        self.assertFalse(outcome.A != 1)

    def test_ne_should_return_true_if_value_not_present(
            self):
        data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        outcome = Outcome(data, identifier='A')
        self.assertTrue(outcome != 4)
