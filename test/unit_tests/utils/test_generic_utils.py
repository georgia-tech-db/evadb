# coding=utf-8
# Copyright 2018-2023 EvaDB
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

from evadb.utils.generic_utils import string_comparison_case_insensitive


class GenericUtilsTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_string_matching_case_insensitive(self):
        """
        A simple test for string_matching_case_insensitve in generic_utils
        used by statement_binder
        """

        test_string_exact_match = string_comparison_case_insensitive(
            "HuggingFace", "HuggingFace"
        )
        test_string_case_insensitive_match = string_comparison_case_insensitive(
            "HuggingFace", "hugGingFaCe"
        )
        test_string_no_match = string_comparison_case_insensitive(
            "HuggingFace", "HuggingFae"
        )
        test_one_string_null = string_comparison_case_insensitive(None, "HuggingFace")
        test_both_strings_null = string_comparison_case_insensitive(None, None)

        self.assertTrue(test_string_exact_match)
        self.assertTrue(test_string_case_insensitive_match)
        self.assertFalse(test_string_no_match)
        self.assertFalse(test_one_string_null)
        self.assertFalse(test_both_strings_null)
